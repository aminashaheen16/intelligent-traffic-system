import sys
sys.path.insert(0, '.')
import asyncio
import base64
import cv2
import os
import shutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from psycopg2.extras import RealDictCursor
from core.database import get_connection
from pipeline import pipeline

app = FastAPI(title="Intelligent Traffic System")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/snapshots", StaticFiles(directory="snapshots"), name="snapshots")

@app.get("/")
def root():
    return FileResponse("dashboard/index.html")

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    os.makedirs("videos", exist_ok=True)
    dest = f"videos/{file.filename}"
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"status": "uploaded", "path": dest, "filename": file.filename}

@app.post("/start")
def start_pipeline(source: str = "0"):
    if pipeline.running:
        pipeline.stop()
        import time; time.sleep(1)
    src = int(source) if source.isdigit() else source
    pipeline.start_async(src)
    return {"status": "started", "source": source}

@app.post("/stop")
def stop_pipeline():
    pipeline.stop()
    return {"status": "stopped"}

@app.get("/stats")
def get_stats():
    return pipeline.stats

@app.get("/violations")
def get_violations(limit: int = 20):
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM violations ORDER BY timestamp DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close(); conn.close()
        return {"violations": [dict(r) for r in rows]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/counts")
def get_counts():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT DATE_TRUNC('hour', timestamp) as hour, COUNT(*) as count
            FROM vehicle_counts GROUP BY hour ORDER BY hour DESC LIMIT 24
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return {"counts": [dict(r) for r in rows]}
    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws/video")
async def video_feed(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if pipeline.current_frame is not None:
                _, buffer = cv2.imencode(".jpg", pipeline.current_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                b64 = base64.b64encode(buffer).decode("utf-8")
                await websocket.send_json({"frame": b64, "stats": pipeline.stats})
            await asyncio.sleep(0.04)
    except WebSocketDisconnect:
        pass

@app.websocket("/ws/stats")
async def stats_feed(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(pipeline.stats)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
