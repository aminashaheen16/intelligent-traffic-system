import sys
sys.path.insert(0, '.')
import cv2
import threading
import time
from core.tracker import VehicleTracker
from core.database import init_db
from modules.vehicle_counter import VehicleCounter
from modules.restricted_area import RestrictedAreaMonitor
from modules.wrong_way import WrongWayDetector
from modules.parking_monitor import ParkingMonitor
from config import ENABLE_COUNTER, ENABLE_RESTRICTED, ENABLE_WRONG_WAY, ENABLE_PARKING

class TrafficPipeline:
    def __init__(self):
        init_db()
        self.tracker = VehicleTracker()

        # Default configs - يتغيروا من الـ Dashboard
        self.counter = VehicleCounter(
            counting_line=[(0, 300), (640, 300)]
        )
        self.restricted = RestrictedAreaMonitor(
            polygon=[(100, 100), (300, 100), (300, 300), (100, 300)]
        )
        self.wrong_way = WrongWayDetector(
            entry_line=[(0, 200), (640, 200)],
            exit_line=[(0, 400), (640, 400)],
            allowed_direction="down"
        )
        self.parking = ParkingMonitor(slots=[
            {"id": 1, "polygon": [(50, 400), (150, 400), (150, 500), (50, 500)]},
            {"id": 2, "polygon": [(160, 400), (260, 400), (260, 500), (160, 500)]},
            {"id": 3, "polygon": [(270, 400), (370, 400), (370, 500), (270, 500)]},
        ])

        self.current_frame = None
        self.stats = {
            "vehicle_count": 0,
            "violations": 0,
            "parking": {"free": 0, "occupied": 0, "total": 0},
            "fps": 0
        }
        self.running = False
        self.source = None

    def process_frame(self, frame):
        tracked = self.tracker.track(frame)

        if ENABLE_COUNTER:
            count = self.counter.update(tracked, frame, str(self.source))
            self.stats["vehicle_count"] = count
            self.counter.draw(frame)

        if ENABLE_RESTRICTED:
            viols = self.restricted.update(tracked, frame, str(self.source))
            if viols:
                self.stats["violations"] += len(viols)
            self.restricted.draw(frame)

        if ENABLE_WRONG_WAY:
            viols = self.wrong_way.update(tracked, frame, str(self.source))
            if viols:
                self.stats["violations"] += len(viols)
            self.wrong_way.draw(frame)

        if ENABLE_PARKING:
            parking_stats = self.parking.update(tracked, frame)
            self.stats["parking"] = parking_stats
            self.parking.draw(frame)

        # Draw bounding boxes + IDs
        for v in tracked:
            x1, y1, x2, y2 = v["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
            cv2.putText(frame, f"ID:{v['track_id']} {v['class_name']}",
                       (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        return frame

    def run(self, source=0):
        self.source = source
        self.running = True
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            print(f"❌ Cannot open source: {source}")
            return

        print(f"✅ Pipeline started on source: {source}")
        prev_time = time.time()

        while self.running:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ End of video or stream lost")
                break

            frame = self.process_frame(frame)

            curr_time = time.time()
            self.stats["fps"] = round(1 / (curr_time - prev_time), 1)
            prev_time = curr_time

            self.current_frame = frame.copy()

        cap.release()
        self.running = False
        print("🛑 Pipeline stopped")

    def start_async(self, source=0):
        t = threading.Thread(target=self.run, args=(source,), daemon=True)
        t.start()
        return t

    def stop(self):
        self.running = False

pipeline = TrafficPipeline()
