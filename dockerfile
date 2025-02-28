FROM python:3.10-slim

# Install required packages: wget, tar, and xz-utils for extracting .tar.xz files
RUN apt-get update && apt-get install -y wget tar xz-utils && rm -rf /var/lib/apt/lists/*

# Download and extract a static ffmpeg binary.
RUN wget -O ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    mkdir /ffmpeg && \
    tar -xJf ffmpeg.tar.xz -C /ffmpeg --strip-components=1 && \
    rm ffmpeg.tar.xz && \
    cp /ffmpeg/ffmpeg /usr/local/bin/ffmpeg && \
    chmod +x /usr/local/bin/ffmpeg && \
    rm -rf /ffmpeg

# Copy and install requirements.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY . /app
WORKDIR /app

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
