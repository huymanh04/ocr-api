# Base Image
FROM python:3.10-slim

# Cài thêm các thư viện hệ thống để paddleocr, opencv chạy được
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Copy source code
COPY . .

# Cài Python package
RUN pip install --no-cache-dir -r requirements.txt

# Mở port 5000
EXPOSE 5000

# Lệnh chạy app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
