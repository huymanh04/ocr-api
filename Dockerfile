# 1. Sử dụng Python image
FROM python:3.11-slim

# 2. Cài Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr

# 3. Đặt thư mục làm việc
WORKDIR /app

# 4. Copy source code
COPY . .

# 5. Cài thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Expose cổng server Flask
EXPOSE 5000

# 7. Lệnh chạy app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
