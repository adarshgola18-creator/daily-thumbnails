"""
Daily thumbnail generator.
Edits the date (and day) text on the two templates and saves the
finished images to /output. Run this once a day (see the GitHub
Actions workflow in .github/workflows/daily.yml).
"""
import datetime, os
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FP = "/usr/share/fonts/truetype/google-fonts/Poppins-%s.ttf"
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
INTER_FP = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
INTER_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
S = 4

def inter_font(weight, size):
    path = INTER_FP % weight
    if not os.path.exists(path):
        path = INTER_FALLBACK
    return ImageFont.truetype(path, size)

TEMPLATES = os.path.join(os.path.dirname(__file__), "templates")
OUTPUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT, exist_ok=True)

def font(weight, size):
    path = FP % weight
    if not os.path.exists(path):
        path = FALLBACK
    return ImageFont.truetype(path, size)

def erase(img_arr, mask_bool, x0, y0, x1, y1, grow=6):
    m = np.zeros(img_arr.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = mask_bool[y0:y1, x0:x1].astype(np.uint8) * 255
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*grow+1, 2*grow+1)))
    return cv2.inpaint(np.clip(img_arr, 0, 255).astype(np.uint8), m, 6, cv2.INPAINT_TELEA).astype(np.float32)

def draw_text(img_arr, text, weight, size, cx, baseline, color, shadow=None, inter=False):
    f = inter_font(weight, size * S) if inter else font(weight, size * S)
    bb = f.getbbox(text, anchor="ls")
    inkw = (bb[2] - bb[0]) / S
    xl = cx - inkw / 2 - bb[0] / S
    X0, Y0 = int(xl) - 20, int(baseline - size * 1.2)
    W, H = int(inkw) + 40, int(size * 1.7)
    m = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(m)
    d.text(((xl - X0) * S, (baseline - Y0) * S), text, font=f, fill=255, anchor="ls")
    m = np.array(m.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255.0
    if shadow:
        dx, dy, a, bl = shadow
        sm = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(bl))
        sm = np.array(sm).astype(np.float32) / 255.0 * a
        reg = img_arr[Y0+dy:Y0+dy+H, X0+dx:X0+dx+W]
        reg[:] = reg * (1 - sm[..., None])
    reg = img_arr[Y0:Y0+H, X0:X0+W]
    reg[:] = reg * (1 - m[..., None]) + np.array(color, np.float32) * m[..., None]
    return img_arr

def make_post_market_update(date_obj, out_path):
    arr = np.array(Image.open(os.path.join(TEMPLATES, "Post_Market_Update_MONDAY.jpg")).convert("RGB")).astype(np.float32)
    R, G, B = arr[..., 0], arr[..., 1], arr[..., 2]
    white = (R > 190) & (G > 190) & (B > 190)
    arr = erase(arr, white, 590, 250, 1210, 315, grow=6)
    txt = f'{date_obj.day} {date_obj.strftime("%B").upper()} \u2019{str(date_obj.year)[2:]}  |  {date_obj.strftime("%A").upper()}'
    arr = draw_text(arr, txt, "Bold", 38, 900, 300, (235, 245, 250))
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(out_path, quality=95)

def make_nifty_analysis(date_obj, out_path):
    arr = np.array(Image.open(os.path.join(TEMPLATES, "Nifty_Analysis_New.jpg")).convert("RGB")).astype(np.float32)

    PILL = (490, 828, 1057, 902)
    RADIUS = 20
    mask = Image.new("L", (arr.shape[1], arr.shape[0]), 0)
    ImageDraw.Draw(mask).rounded_rectangle(PILL, radius=RADIUS, fill=255)
    mask = np.array(mask).astype(np.float32) / 255.0
    arr = arr * (1 - mask[..., None]) + np.array([255, 255, 255], np.float32) * mask[..., None]

    cx = (PILL[0] + PILL[2]) / 2
    baseline = (PILL[1] + PILL[3]) / 2 + 13

    txt = f'{date_obj.strftime("%A")}, {date_obj.day} {date_obj.strftime("%B")} \u2019{str(date_obj.year)[2:]}'
    arr = draw_text(arr, txt, "Medium", 36, cx, baseline, (25, 25, 25), inter=True)
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(out_path, quality=95)

if __name__ == "__main__":
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)).date() + datetime.timedelta(days=1)
    p1 = os.path.join(OUTPUT, "Post_Market_Update.jpg")
    p2 = os.path.join(OUTPUT, "Nifty_Analysis.jpg")
    make_post_market_update(today, p1)
    make_nifty_analysis(today, p2)
    print("Generated:", p1, p2)
