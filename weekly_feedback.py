"""
Weekly Analysis images: changes the label in the white box ("3rd Week of Oct")
on the landscape and vertical images, then emails both to the recipients.
Triggered every Friday 4 PM IST by the GitHub workflow weekly-feedback.yml.
"""
import datetime, os, smtplib, sys
import numpy as np
from email.message import EmailMessage
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(BASE, "templates")
OUTPUT = os.path.join(BASE, "output_weekly")
os.makedirs(OUTPUT, exist_ok=True)

INTER = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
S = 4  # supersampling

# box = (left, top, right, bottom) of the white label box measured on each template,
# size = font size that reproduces the original text width.
IMAGES = [
    {"template": "Weekly_Analysis_Landscape.jpg", "out": "Weekly_Analysis_Landscape.jpg",
     "box": (654, 930, 1288, 1046), "size": 72.7, "baseline": 1015},
    {"template": "Weekly_Analysis_Vertical.jpg", "out": "Weekly_Analysis_Vertical.jpg",
     "box": (171, 1495, 909, 1629), "size": 84.6, "baseline": 1594},
]

def ordinal(n):
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(n, f"{n}th")

def week_label(today):
    """Label for the week that is ending: uses that week's Friday.
    Friday date 1-7 -> 1st week, 8-14 -> 2nd, 15-21 -> 3rd, 22-28 -> 4th, 29+ -> 5th."""
    friday = today + datetime.timedelta(days=4 - today.weekday())
    return f"{ordinal((friday.day - 1) // 7 + 1)} Week of {friday.strftime('%b')}"

def draw_label(cfg, label, out_path):
    arr = np.array(Image.open(os.path.join(TEMPLATES, cfg["template"])).convert("RGB")).astype(np.float32)
    x0, y0, x1, y1 = cfg["box"]
    # wipe the old text: fill the inside of the white box (keep a 5px margin so the box edge stays)
    arr[y0 + 5:y1 - 4, x0 + 5:x1 - 4] = 255.0

    path = INTER if os.path.exists(INTER) else FALLBACK
    size = cfg["size"]
    max_w = (x1 - x0) - 60
    while True:  # shrink only if a longer label would not fit
        f = ImageFont.truetype(path, int(size * S))
        bb = f.getbbox(label, anchor="ls")
        w = (bb[2] - bb[0]) / S
        if w <= max_w:
            break
        size -= 1
    cx = (x0 + x1) / 2
    xl = cx - w / 2 - bb[0] / S
    pad = 20
    X0, Y0 = int(xl) - pad, int(cfg["baseline"] - size * 1.1)
    W, H = int(w) + 2 * pad + 4, int(size * 1.5)
    m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(m).text(((xl - X0) * S, (cfg["baseline"] - Y0) * S), label, font=f, fill=255, anchor="ls")
    m = np.array(m.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255.0
    reg = arr[Y0:Y0 + H, X0:X0 + W]
    reg[:] = reg * (1 - m[..., None]) + np.array([0, 0, 0], np.float32) * m[..., None]
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(out_path, quality=95, subsampling=0)

def send_mail(label, files):
    user = os.environ["GMAIL_USER"]
    pwd = os.environ["GMAIL_APP_PASSWORD"]
    to = os.environ["FEEDBACK_TO_ADDRESSES"]
    msg = EmailMessage()
    msg["Subject"] = f"Weekly Analysis - {label}"
    msg["From"] = user
    msg["To"] = to
    msg.set_content(f"Hi,\n\nPlease find attached the Weekly Analysis images for the {label}.\n\nThanks")
    for p in files:
        with open(p, "rb") as fh:
            msg.add_attachment(fh.read(), maintype="image", subtype="jpeg", filename=os.path.basename(p))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(user, pwd)
        smtp.send_message(msg)
    print("Email sent")

if __name__ == "__main__":
    today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)).date()
    label = os.environ.get("LABEL_OVERRIDE") or week_label(today)
    print("Label:", label)
    files = []
    for cfg in IMAGES:
        out = os.path.join(OUTPUT, cfg["out"])
        draw_label(cfg, label, out)
        files.append(out)
    if os.environ.get("SKIP_EMAIL") == "1":
        print("Skipping email (test mode)")
        sys.exit(0)
    send_mail(label, files)
