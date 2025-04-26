import base64
import cv2
import numpy as np
from paddleocr import PaddleOCR
from flask import Flask, request, jsonify
from PIL import Image
import logging

# Bật debug log để hiện lỗi
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Load PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

def ocr_from_base64(b64_string: str):
    if ',' in b64_string:
        b64_string = b64_string.split(',', 1)[1]
    
    img_data = base64.b64decode(b64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Không thể giải mã ảnh từ Base64")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

   # OCR nhận diện văn bản từ ảnh
    result = ocr.ocr(thresh, cls=True)

    # Kiểm tra kết quả
    if not result or result[0] is None:
        # Không có dòng nào được phát hiện
        return "", img, []

    page = result[0]  # page là một list các tuple (bbox, (text, score))

    # Nếu page là None hoặc rỗng, trả về chuỗi trống
    if not page:
        return "", img, []

    # Gộp các ký tự và bỏ khoảng trắng
    # chú ý page có dạng [ ( [x1,y1...], (text,score) ), ... ]
    chars = [ item[1][0] for item in page if item and item[1] and item[1][0] ]
    captcha = "".join(chars).replace(" ", "")
    return captcha, img, page

@app.route('/ocr', methods=['POST'])
def ocr_api():
    data = request.json
    b64_string = data.get("base64", "")
    
    if not b64_string:
        return jsonify({"error": "Missing base64 string"}), 400
    
    try:
        captcha, img, page = ocr_from_base64(b64_string)
        # Trả về captcha (chuỗi rỗng nếu không nhận diện được)
        return jsonify({"captcha": captcha})
    except Exception as e:
        app.logger.error(f"Lỗi OCR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
