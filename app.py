import base64
import cv2
import numpy as np
from paddleocr import PaddleOCR, draw_ocr
import matplotlib.pyplot as plt

FONT_PATH = "C:/Windows/Fonts/arial.ttf"
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

def ocr_from_base64(b64_string: str):
    # Bỏ tiền tố nếu có data URI
    if ',' in b64_string:
        b64_string = b64_string.split(',', 1)[1]
    # Giải mã
    img_data = base64.b64decode(b64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Không thể giải mã ảnh từ Base64")
    # Tiền xử lý
    gray = cv2.cvtColor(img, cv2.COLORBGR2GRAY)
    , thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESHOTSU)
    # OCR
    result = ocr.ocr(thresh, cls=True)
    page = result[0]
    # Gộp ký tự, bỏ khoảng trắng
    chars = [t for , (t, _) in page]
    captcha = "".join(chars).replace(" ", "")
    return captcha, img, page

if name == "main":
    # Đọc Base64 từ bàn phím
    b64 = input("Paste chuỗi Base64 của ảnh captcha rồi nhấn Enter:\n").strip()

    captcha, img, page = ocr_frombase64(b64)
    print("Captcha cuối cùng:", captcha)

    # Vẽ kết quả
    boxes = [b for b, in page]
    texts = [t for ,(t,) in page]
    scores = [s for ,(,s) in page]
    vis = draw_ocr(img, boxes, texts, scores, font_path=FONT_PATH)

    plt.figure(figsize=(6,2))
    plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.tight_layout()
    plt.show()
