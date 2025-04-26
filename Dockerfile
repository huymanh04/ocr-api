# 1. Base image
FROM python:3.10-slim

# 2. Cài thư viện hệ thống
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# 3. Thư mục làm việc
WORKDIR /app

# 4. Copy source
COPY . .

# 5. Cài Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 6. Expose port
EXPOSE 5000

# 7. Chạy app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
