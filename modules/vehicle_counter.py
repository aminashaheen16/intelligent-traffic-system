import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
from datetime import datetime
from core.database import get_connection

class VehicleCounter:
    def __init__(self, counting_line=None):
        # counting_line = [(x1,y1), (x2,y2)]
        self.counting_line = counting_line
        self.counted_ids = set()
        self.count = 0
        self.prev_centers = {}

    def set_line(self, line):
        self.counting_line = line

    def _crosses_line(self, prev_center, curr_center, line):
        if line is None:
            return False
        (lx1, ly1), (lx2, ly2) = line
        def side(px, py):
            return (lx2 - lx1) * (py - ly1) - (ly2 - ly1) * (px - lx1)
        s1 = side(prev_center[0], prev_center[1])
        s2 = side(curr_center[0], curr_center[1])
        return (s1 > 0) != (s2 > 0)

    def update(self, tracked_vehicles, frame, video_source=""):
        for v in tracked_vehicles:
            tid = v["track_id"]
            curr = v["center"]

            if tid in self.prev_centers:
                prev = self.prev_centers[tid]
                if tid not in self.counted_ids:
                    if self._crosses_line(prev, curr, self.counting_line):
                        self.counted_ids.add(tid)
                        self.count += 1
                        self._save_to_db(v["class_name"], video_source)

            self.prev_centers[tid] = curr

        return self.count

    def _save_to_db(self, vehicle_type, video_source):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO vehicle_counts (vehicle_type, video_source) VALUES (%s, %s)",
                (vehicle_type, video_source)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"DB Error: {e}")

    def draw(self, frame):
        if self.counting_line:
            cv2.line(frame, self.counting_line[0], self.counting_line[1], (0, 255, 255), 2)
        cv2.putText(frame, f"Count: {self.count}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        return frame
