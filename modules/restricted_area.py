import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
import os
from datetime import datetime
from core.database import get_connection
from alerts.email_service import send_alert_email
from config import SNAPSHOT_DIR

class RestrictedAreaMonitor:
    def __init__(self, polygon=None):
        self.polygon = np.array(polygon) if polygon else None
        self.alerted_ids = set()
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    def set_polygon(self, polygon):
        self.polygon = np.array(polygon)

    def _in_zone(self, center):
        if self.polygon is None:
            return False
        return cv2.pointPolygonTest(self.polygon, center, False) >= 0

    def update(self, tracked_vehicles, frame, video_source=""):
        violations = []
        for v in tracked_vehicles:
            tid = v["track_id"]
            if tid not in self.alerted_ids and self._in_zone(v["center"]):
                self.alerted_ids.add(tid)
                snapshot = self._save_snapshot(frame, tid)
                self._save_to_db(v["class_name"], snapshot, video_source)
                send_alert_email("Restricted Area Violation",
                    f"Vehicle {v['class_name']} entered restricted area at {datetime.now()}", snapshot)
                violations.append(v)
        return violations

    def _save_snapshot(self, frame, tid):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SNAPSHOT_DIR, f"restricted_{tid}_{ts}.jpg")
        cv2.imwrite(path, frame)
        return path

    def _save_to_db(self, vehicle_type, snapshot_path, video_source):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO violations (violation_type, vehicle_type, snapshot_path, video_source) VALUES (%s, %s, %s, %s)",
                ("restricted_area", vehicle_type, snapshot_path, video_source)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"DB Error: {e}")

    def draw(self, frame):
        if self.polygon is not None:
            overlay = frame.copy()
            cv2.fillPoly(overlay, [self.polygon], (0, 0, 255))
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            cv2.polylines(frame, [self.polygon], True, (0, 0, 255), 2)
        return frame
