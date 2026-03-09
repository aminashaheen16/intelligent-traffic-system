import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
import os
from datetime import datetime
from core.database import get_connection
from alerts.email_service import send_alert_email
from config import SNAPSHOT_DIR

class WrongWayDetector:
    def __init__(self, entry_line=None, exit_line=None, allowed_direction="down"):
        self.entry_line = entry_line
        self.exit_line = exit_line
        self.allowed_direction = allowed_direction
        self.crossed_entry = {}
        self.alerted_ids = set()
        self.prev_centers = {}
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    def _crosses_line(self, prev, curr, line):
        if line is None:
            return False
        (lx1, ly1), (lx2, ly2) = line
        def side(px, py):
            return (lx2-lx1)*(py-ly1) - (ly2-ly1)*(px-lx1)
        return (side(*prev) > 0) != (side(*curr) > 0)

    def update(self, tracked_vehicles, frame, video_source=""):
        violations = []
        for v in tracked_vehicles:
            tid = v["track_id"]
            curr = v["center"]

            if tid in self.prev_centers:
                prev = self.prev_centers[tid]

                if self._crosses_line(prev, curr, self.entry_line):
                    self.crossed_entry[tid] = curr[1]

                if tid in self.crossed_entry and tid not in self.alerted_ids:
                    if self._crosses_line(prev, curr, self.exit_line):
                        entry_y = self.crossed_entry[tid]
                        curr_y = curr[1]
                        going_down = curr_y > entry_y
                        is_wrong = (self.allowed_direction == "down" and not going_down) or \
                                   (self.allowed_direction == "up" and going_down)
                        if is_wrong:
                            self.alerted_ids.add(tid)
                            snapshot = self._save_snapshot(frame, tid)
                            self._save_to_db(v["class_name"], snapshot, video_source)
                            send_alert_email("Wrong Way Violation",
                                f"Vehicle {v['class_name']} going wrong way at {datetime.now()}", snapshot)
                            violations.append(v)

            self.prev_centers[tid] = curr
        return violations

    def _save_snapshot(self, frame, tid):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SNAPSHOT_DIR, f"wrongway_{tid}_{ts}.jpg")
        cv2.imwrite(path, frame)
        return path

    def _save_to_db(self, vehicle_type, snapshot_path, video_source):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO violations (violation_type, vehicle_type, snapshot_path, video_source) VALUES (%s, %s, %s, %s)",
                ("wrong_way", vehicle_type, snapshot_path, video_source)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"DB Error: {e}")

    def draw(self, frame):
        if self.entry_line:
            cv2.line(frame, self.entry_line[0], self.entry_line[1], (0, 255, 0), 2)
            cv2.putText(frame, "ENTRY", self.entry_line[0], cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        if self.exit_line:
            cv2.line(frame, self.exit_line[0], self.exit_line[1], (0, 0, 255), 2)
            cv2.putText(frame, "EXIT", self.exit_line[0], cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
        return frame
