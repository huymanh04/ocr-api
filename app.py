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

# Khởi tạo PaddleOCR (CPU)
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

def ocr_from_base64(b64_string: str) -> str:
    # Bỏ tiền tố data URI nếu có
    if ',' in b64_string:
        b64_string = b64_string.split(',', 1)[1]

    # Giải mã Base64 thành bytes
    img_data = base64.b64decode(b64_string)
    # Bytes → numpy array → decode thành ảnh
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Không thể giải mã ảnh từ Base64")

    # Chuyển sang grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Gọi PaddleOCR trực tiếp lên ảnh gray
    result = ocr.ocr(gray, cls=True)

    # Nếu không có kết quả, trả về chuỗi rỗng
    if not result or not result[0]:
        return ""

    # result[0] là list [(bbox, (text,score)), ...]
    page = result[0]

    # Gom text, bỏ khoảng trắng
    chars = [ item[1][0] for item in page if item and item[1] ]
    return "".join(chars).replace(" ", "")

@app.route('/ocr', methods=['POST'])
def ocr_api():
    data = request.get_json(silent=True) or {}
    b64 = data.get("base64", "")

    if not b64:
        return jsonify({"error": "Missing base64"}), 400

    try:
        captcha = ocr_from_base64(b64)
        return jsonify({"captcha": captcha})
    except Exception as ex:
        app.logger.error(f"Lỗi OCR: {ex}")
        return jsonify({"error": str(ex)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
