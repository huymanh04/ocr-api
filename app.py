import base64
import cv2
import numpy as np
from paddleocr import PaddleOCR, draw_ocr
from flask import Flask, request, jsonify
import logging

# Bật debug log để hiện lỗi
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)


def ocr_from_base64(b64_string: str):
    # Bỏ tiền tố data URI nếu có
    if ',' in b64_string:
        b64_string = b64_string.split(',', 1)[1]

    # Giải mã Base64 thành ảnh
    img_data = base64.b64decode(b64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Không thể giải mã ảnh từ Base64")

    # Preprocess: chuyển sang grayscale và threshold Otsu
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Tiền xử lý resize nếu ảnh nhỏ
    h, w = thresh.shape[:2]
    if w < 200:
        thresh = cv2.resize(thresh, (w*2, h*2), interpolation=cv2.INTER_CUBIC)

    # Chuyển sang RGB vì PaddleOCR hoạt động tốt với imagenet format
    rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)

    # OCR nhận diện văn bản từ ảnh
    result = ocr.ocr(rgb, cls=True)
    logging.debug(f"PaddleOCR raw result: {result}")

    if not result or not result[0]:
        return ""

    page = result[0]  # list of (bbox, (text, score))
    # Gộp ký tự, bỏ khoảng trắng
    chars = [text for _, (text, _) in page]
    return "".join(chars).replace(" ", "")


@app.route('/ocr', methods=['POST'])
def ocr_api():
    data = request.get_json(silent=True) or {}
    b64_string = data.get("base64", "")
    if not b64_string:
        return jsonify({"error": "Missing base64 string"}), 400

    try:
        captcha = ocr_from_base64(b64_string)
        return jsonify({"captcha": captcha})
    except Exception as e:
        app.logger.error(f"Lỗi OCR: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Chạy debug local
    app.run(host="0.0.0.0", port=5000, debug=True)
