import base64
import cv2
import numpy as np
from paddleocr import PaddleOCR
from flask import Flask, request, jsonify
import logging

# Bật debug log
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='en',
    use_gpu=False,
    det_db_box_thresh=0.3,  # giảm ngưỡng detect box cho ảnh bé
)

def preprocess_image(img):
    """Tiền xử lý ảnh để PaddleOCR dễ đọc hơn"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Adaptive Threshold giúp tách nền tốt hơn Otsu cho ảnh nhiễu
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    # Resize lớn hơn nếu ảnh nhỏ (giúp OCR chính xác hơn)
    h, w = thresh.shape
    if min(h, w) < 300:
        scale = 300.0 / min(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        thresh = cv2.resize(thresh, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # Biến thành ảnh RGB
    rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
    return rgb

def ocr_from_base64(b64_string: str):
    """Nhận base64 string và trả về text OCR"""
    if ',' in b64_string:
        b64_string = b64_string.split(',', 1)[1]

    try:
        img_data = base64.b64decode(b64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        raise ValueError("Base64 không hợp lệ hoặc không giải mã được ảnh.") from e

    if img is None:
        raise ValueError("Không thể giải mã ảnh từ Base64.")

    processed_img = preprocess_image(img)

    result = ocr.ocr(processed_img, cls=True)
    logging.debug(f"PaddleOCR raw result: {result}")

    if not result or not result[0]:
        return ""

    # Gộp text đọc được
    texts = [text_info[1][0] for text_info in result[0] if text_info[1][0].strip()]
    final_text = "".join(texts).replace(" ", "").strip()

    return final_text

@app.route('/ocr', methods=['POST'])
def ocr_api():
    data = request.get_json(silent=True) or {}
    b64_string = data.get("base64", "")
    if not b64_string:
        return jsonify({"error": "Missing base64 string"}), 400

    try:
        captcha_text = ocr_from_base64(b64_string)
        return jsonify({"captcha": captcha_text})
    except Exception as e:
        app.logger.error(f"Lỗi OCR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
