from ultralytics import YOLO
import cv2
import sys
sys.path.insert(0, '.')
from config import YOLO_MODEL, VEHICLE_CLASSES, CONFIDENCE_THRESHOLD

class VehicleDetector:
    def __init__(self):
        self.model = YOLO(YOLO_MODEL)
        self.vehicle_classes = VEHICLE_CLASSES
        self.confidence = CONFIDENCE_THRESHOLD
        self.class_names = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

    def detect(self, frame):
        results = self.model(frame, conf=self.confidence, verbose=False)[0]
        detections = []
        for box in results.boxes:
            cls = int(box.cls[0])
            if cls in self.vehicle_classes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                detections.append({
                    "bbox": (x1, y1, x2, y2),
                    "class_id": cls,
                    "class_name": self.class_names.get(cls, "vehicle"),
                    "confidence": conf,
                    "center": ((x1 + x2) // 2, (y1 + y2) // 2)
                })
        return detections
