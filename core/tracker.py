import sys
sys.path.insert(0, '.')
from ultralytics.trackers import BYTETracker
from ultralytics import YOLO
import numpy as np
from config import YOLO_MODEL, VEHICLE_CLASSES, CONFIDENCE_THRESHOLD

class VehicleTracker:
    def __init__(self):
        self.model = YOLO(YOLO_MODEL)
        self.vehicle_classes = VEHICLE_CLASSES
        self.confidence = CONFIDENCE_THRESHOLD
        self.class_names = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

    def track(self, frame):
        results = self.model.track(
            frame,
            conf=self.confidence,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )[0]

        tracked = []
        if results.boxes.id is None:
            return tracked

        for box, track_id in zip(results.boxes, results.boxes.id):
            cls = int(box.cls[0])
            if cls in self.vehicle_classes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                tracked.append({
                    "track_id": int(track_id),
                    "bbox": (x1, y1, x2, y2),
                    "class_id": cls,
                    "class_name": self.class_names.get(cls, "vehicle"),
                    "confidence": float(box.conf[0]),
                    "center": ((x1 + x2) // 2, (y1 + y2) // 2)
                })
        return tracked
