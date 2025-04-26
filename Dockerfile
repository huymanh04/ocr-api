# Sử dụng image Python nhẹ
FROM python:3.11-slim

# Cài đặt Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr

# Tạo thư mục làm việc
WORKDIR /app

# Copy toàn bộ source code vào container
COPY . .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Mở cổng 5000
EXPOSE 5000

# Lệnh khởi động app bằng gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
