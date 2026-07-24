# Gunakan image Python yang ringan
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg, libgl1 untuk OpenCV, dll)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Salin file requirements.txt
COPY requirements.txt .

# Install pustaka Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file source code ke dalam container
COPY . .

# Ekspose port default Streamlit
EXPOSE 8501

# Jalankan aplikasi Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
