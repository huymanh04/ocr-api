from flask import Flask, request, jsonify
import base64
from PIL import Image
from io import BytesIO
import pytesseract
import base64
import cv2
import numpy as np
from paddleocr import PaddleOCR, draw_ocr
import matplotlib.pyplot as plt
app = Flask(__name__)

# Cấu hình đúng đường dẫn tesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
FONT_PATH = "C:/Windows/Fonts/arial.ttf"
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

@app.route("/ocr", methods=["POST"])
def ocr():
    data = request.json
    base64_str = data.get("base64", "")
    if not base64_str:
        return jsonify({"error": "missing base64"}), 400

    try:
      
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
        return captcha
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
