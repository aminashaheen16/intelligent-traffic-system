import sys
sys.path.insert(0, '.')
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER, SMTP_HOST, SMTP_PORT
import os

def send_alert_email(subject, body, image_path=None):
    try:
        if not EMAIL_SENDER or not EMAIL_PASSWORD:
            print(f"📧 Email skipped (no credentials): {subject}")
            return

        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = f"🚨 Traffic Alert: {subject}"
        msg.attach(MIMEText(body, "plain"))

        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                img = MIMEImage(f.read())
                img.add_header("Content-Disposition", "attachment", filename=os.path.basename(image_path))
                msg.attach(img)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent: {subject}")
    except Exception as e:
        print(f"❌ Email error: {e}")
