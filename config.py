import os
from dotenv import load_dotenv

load_dotenv()

# Database
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "traffic_db")
DB_USER = os.getenv("DB_USER", "aminashaheen")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Email
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# App
SNAPSHOT_DIR = os.getenv("SNAPSHOT_DIR", "snapshots")
VIDEO_DIR = os.getenv("VIDEO_DIR", "videos")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# YOLO
YOLO_MODEL = "yolo11n.pt"
VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck
CONFIDENCE_THRESHOLD = 0.5

# Modules toggle
ENABLE_COUNTER = True
ENABLE_RESTRICTED = True
ENABLE_WRONG_WAY = True
ENABLE_PARKING = True
