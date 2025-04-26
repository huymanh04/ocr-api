# Sử dụng image Python base
FROM python:3.11-slim

# Cài đặt các phụ thuộc hệ thống cần thiết
RUN apt-get update && apt-get install -y tesseract-ocr

# Cài đặt các thư viện Python cần thiết
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Copy mã nguồn của bạn vào container
COPY . /app

# Chạy ứng dụng Flask
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
