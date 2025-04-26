import base64
import cv2
import numpy as np
from paddleocr import PaddleOCR
from flask import Flask, request, jsonify
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
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

    h, w = thresh.shape[:2]
    if w < 200:
        thresh = cv2.resize(thresh, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

    rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)

    result = ocr.ocr(rgb, cls=True)
    logging.debug(f"PaddleOCR raw result: {result}")

    if not result or not result[0]:
        return "", None

    page = result[0]
    boxes = [line[0] for line in page]
    txts = [line[1][0] for line in page]
    scores = [line[1][1] for line in page]

    # Vẽ lại ảnh
    from paddleocr import draw_ocr
    im_show = draw_ocr(rgb, boxes, txts, scores, font_path='fonts/simfang.ttf')  # nhớ có font
    im_show = cv2.cvtColor(im_show, cv2.COLOR_RGB2BGR)

    # Encode ảnh debug thành base64
    _, buffer = cv2.imencode('.jpg', im_show)
    debug_base64 = base64.b64encode(buffer).decode('utf-8')

    # Gộp text
    captcha = "".join(txts).replace(" ", "")

    return captcha, debug_base64

@app.route('/ocr', methods=['POST'])
def ocr_api():
    data = request.get_json(silent=True) or {}
    b64_string = data.get("base64", "")
    if not b64_string:
        return jsonify({"error": "Missing base64 string"}), 400

    try:
        captcha, debug_img_base64 = ocr_from_base64(b64_string)
        return jsonify({
            "captcha": captcha,
       "debug_image_base64": "data:image/jpeg;base64," + (debug_img_base64 or "")
    
        })
    except Exception as e:
        app.logger.error(f"Lỗi OCR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
