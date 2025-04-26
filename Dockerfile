# 1. Sử dụng Python slim (nhẹ)
FROM python:3.10-slim

# 2. Cài các gói cần thiết cho PaddleOCR
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-glx \
    wget \
    && apt-get clean

# 3. Đặt thư mục làm việc
WORKDIR /app

# 4. Copy source code vào container
COPY . .

# 5. Cài thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Mở cổng 5000
EXPOSE 5000

# 7. Lệnh khởi động app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
