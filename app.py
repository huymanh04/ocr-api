from flask import Flask, request, jsonify
import base64
from PIL import Image
from io import BytesIO
import pytesseract

app = Flask(__name__)

# Cấu hình đường dẫn Tesseract nếu cần thiết
pytesseract.pytesseract.tesseract_cmd = "tesseract-ocr"

@app.route("/ocr", methods=["POST"])
def ocr():
    data = request.json
    base64_str = data.get("base64", "")
    if not base64_str:
        return jsonify({"error": "missing base64"}), 400

    try:
        image_data = base64.b64decode(base64_str)
        image = Image.open(BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        return jsonify({"text": text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
