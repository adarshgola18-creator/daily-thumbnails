"""Emails the two generated images as attachments using Gmail SMTP."""
import os, glob, smtplib
from email.message import EmailMessage

GMAIL_USER = os.environ["GMAIL_USER"]          # your full gmail address
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]  # 16-char App Password, not your login password
TO_ADDRESSES = os.environ["TO_ADDRESSES"]      # comma-separated, e.g. "a@x.com,b@y.com"
OUTPUT = os.path.join(os.path.dirname(__file__), "output")

msg = EmailMessage()
msg["Subject"] = "Today's Thumbnails"
msg["From"] = GMAIL_USER
msg["To"] = TO_ADDRESSES
msg.set_content("Attached: today's thumbnails.")

for path in glob.glob(os.path.join(OUTPUT, "*.jpg")):
    with open(path, "rb") as f:
        msg.add_attachment(f.read(), maintype="image", subtype="jpeg", filename=os.path.basename(path))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    smtp.send_message(msg)

print("Email sent to", TO_ADDRESSES)
