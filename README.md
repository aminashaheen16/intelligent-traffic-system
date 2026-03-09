# 🚗 Intelligent Traffic & Parking Monitoring System

A real-time AI-powered traffic monitoring platform using YOLOv11 and ByteTrack.

## 📹 Demo
[Watch Demo](demo/system-demo.mov)

## ✅ Features
- **Vehicle Counter** – counts vehicles crossing a virtual line
- **Restricted Area Monitor** – detects violations + email alerts
- **Wrong Way Detection** – identifies wrong-direction vehicles
- **Parking Monitor** – real-time free/occupied slot tracking
- **Live Dashboard** – WebSocket video stream + charts

## 🛠 Tech Stack
`YOLOv11` `ByteTrack` `FastAPI` `PostgreSQL` `OpenCV` `Docker`

## 🚀 Run Locally
```bash
git clone https://github.com/aminashaheen16/intelligent-traffic-system
cd intelligent-traffic-system
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn api.main:app --host 0.0.0.0 --port 8000
```
Open http://localhost:8000

## 📁 Project Structure
```
core/       → YOLO detector + ByteTrack tracker + Database
modules/    → 4 analysis modules
api/        → FastAPI backend + WebSocket
dashboard/  → Live web UI
alerts/     → Email notifications
```
