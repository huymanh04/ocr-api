import base64
import cv2
import numpy as np
from paddleocr import PaddleOCR, draw_ocr
from flask import Flask, request, jsonify
import matplotlib.pyplot as plt
import io
from PIL import Image

app = Flask(__name__)

# Cấu hình PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

def ocr_from_base64(b64_string: str):
    # Bỏ tiền tố nếu có data URI
    if ',' in b64_string:
        b64_string = b64_string.split(',', 1)[1]
    
    # Giải mã Base64
    img_data = base64.b64decode(b64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Không thể giải mã ảnh từ Base64")

    # Tiền xử lý ảnh
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # OCR nhận diện văn bản từ ảnh
    result = ocr.ocr(thresh, cls=True)
    page = result[0]

    # Gộp các ký tự và bỏ khoảng trắng
    chars = [t for (t, _) in page]
    captcha = "".join(chars).replace(" ", "")
    return captcha, img, page

@app.route('/ocr', methods=['POST'])
def ocr_api():
    # Lấy Base64 từ request
    data = request.json
    b64_string = data.get("base64", "")
    
    if not b64_string:
        return jsonify({"error": "Missing base64 string"}), 400
    
    try:
        # Nhận diện captcha từ Base64
        captcha, img, page = ocr_from_base64(b64_string)
        
        # Trả về captcha nhận được
        return jsonify({"captcha": captcha})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
