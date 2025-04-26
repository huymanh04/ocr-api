import base64
import cv2
import numpy as np
from paddleocr import PaddleOCR
from flask import Flask, request, jsonify
import logging

# Bật debug log để xem trong Render logs
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Khởi tạo PaddleOCR (CPU)
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

def ocr_from_base64(b64_string: str) -> str:
    # Bỏ tiền tố data URI nếu có
    if ',' in b64_string:
        b64_string = b64_string.split(',', 1)[1]

    # Giải mã Base64
    img_data = base64.b64decode(b64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Không thể giải mã ảnh từ Base64")

    # Thử OCR trực tiếp trên ảnh gốc (BGR)
    result = ocr.ocr(img, cls=True)
    app.logger.debug(f"PaddleOCR raw result: {result}")

    # Nếu không có kết quả
    if not result or not result[0]:
        return "heheh"

    # result[0] là list [(bbox, (text,score)), ...]
    page = result[0]

    # Gom text, bỏ khoảng trắng
    chars = [ text for (_, (text, _)) in page ]
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
