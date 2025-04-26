# 1. Sử dụng Python image nhẹ
FROM python:3.10-slim

# 2. Cài đặt PaddleOCR và các thư viện phụ thuộc
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3. Đặt thư mục làm việc
WORKDIR /app

# 4. Copy source code vào container
COPY . .

# 5. Cài thư viện Python từ file requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 6. Expose cổng server Flask
EXPOSE 5000

# 7. Lệnh chạy app bằng gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
