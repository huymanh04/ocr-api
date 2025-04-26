import base64
import cv2
import numpy as np
from paddleocr import PaddleOCR, draw_ocr
from flask import Flask, request, jsonify
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

def preprocess_image(img):
    # Resize lớn nếu ảnh bé
    h, w = img.shape[:2]
    if w < 400:
        scale = 400 / w
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

    # Chuyển grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Xử lý Threshold - làm rõ text
    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # Morphology để làm nét chữ
    kernel = np.ones((2,2), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Chuyển lại thành RGB
    rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)

    return rgb

def ocr_from_base64(b64_string: str):
    if ',' in b64_string:
        b64_string = b64_string.split(',', 1)[1]

    img_data = base64.b64decode(b64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode base64 to image.")

    # Preprocess ảnh
    processed_img = preprocess_image(img)

    # OCR
    result = ocr.ocr(processed_img, cls=True)
    logging.debug(f"PaddleOCR result: {result}")

    if not result or not result[0]:
        return "", None

    boxes = [line[0] for line in result[0]]
    txts = [line[1][0] for line in result[0]]
    scores = [line[1][1] for line in result[0]]

    # Gộp text
    text_result = ''.join(txts).replace(" ", "")

    # Vẽ lại ảnh
    image_with_box = draw_ocr(img, boxes, txts, scores, font_path='PaddleOCR/doc/fonts/simfang.ttf')
    image_with_box = cv2.cvtColor(image_with_box, cv2.COLOR_RGB2BGR)

    # Encode ảnh sau khi vẽ thành base64
    _, buffer = cv2.imencode('.jpg', image_with_box)
    b64_output = base64.b64encode(buffer).decode('utf-8')

    return text_result, b64_output

@app.route('/ocr', methods=['POST'])
def ocr_api():
    data = request.get_json(silent=True) or {}
    b64_string = data.get("base64", "")
    if not b64_string:
        return jsonify({"error": "Missing base64 string"}), 400

    try:
        captcha, img_b64 = ocr_from_base64(b64_string)
        return jsonify({
            "captcha": captcha,
            "image_with_box": f"data:image/jpeg;base64,{img_b64}"
        })
    except Exception as e:
        app.logger.error(f"Lỗi OCR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
