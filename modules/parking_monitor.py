import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
from datetime import datetime
from core.database import get_connection

class ParkingMonitor:
    def __init__(self, slots=None):
        # slots = [{"id": 1, "polygon": [(x1,y1),...]}]
        self.slots = slots or []
        self.slot_status = {}
        self.stable_count = {}

    def set_slots(self, slots):
        self.slots = slots

    def _in_slot(self, center, polygon):
        poly = np.array(polygon)
        return cv2.pointPolygonTest(poly, center, False) >= 0

    def update(self, tracked_vehicles, frame):
        occupied_ids = set()
        for v in tracked_vehicles:
            for slot in self.slots:
                if self._in_slot(v["center"], slot["polygon"]):
                    occupied_ids.add(slot["id"])

        for slot in self.slots:
            sid = slot["id"]
            new_status = "occupied" if sid in occupied_ids else "free"
            self.stable_count[sid] = self.stable_count.get(sid, 0)

            if new_status == self.slot_status.get(sid):
                self.stable_count[sid] += 1
            else:
                self.stable_count[sid] = 0

            if self.stable_count[sid] >= 3:
                if self.slot_status.get(sid) != new_status:
                    self.slot_status[sid] = new_status
                    self._save_to_db(sid, new_status)

        free = sum(1 for s in self.slot_status.values() if s == "free")
        total = len(self.slots)
        return {"free": free, "occupied": total - free, "total": total}

    def _save_to_db(self, slot_id, status):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO parking_status (slot_id, status) VALUES (%s, %s)",
                (slot_id, status)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"DB Error: {e}")

    def draw(self, frame):
        for slot in self.slots:
            sid = slot["id"]
            status = self.slot_status.get(sid, "free")
            color = (0, 0, 255) if status == "occupied" else (0, 255, 0)
            poly = np.array(slot["polygon"])
            overlay = frame.copy()
            cv2.fillPoly(overlay, [poly], color)
            cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
            cv2.polylines(frame, [poly], True, color, 2)
            cx = sum(p[0] for p in slot["polygon"]) // len(slot["polygon"])
            cy = sum(p[1] for p in slot["polygon"]) // len(slot["polygon"])
            cv2.putText(frame, f"P{sid}", (cx-10, cy),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        return frame
