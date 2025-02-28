# Use an official lightweight Python image
FROM python:3.10-slim

# Install required tools
RUN apt-get update && apt-get install -y wget tar unzip && rm -rf /var/lib/apt/lists/*

# Download and extract a statically linked ffmpeg binary.
# (Make sure the URL points to a valid static build for your platform.)
RUN wget -O ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    mkdir /ffmpeg && \
    tar -xJf ffmpeg.tar.xz -C /ffmpeg --strip-components=1 && \
    rm ffmpeg.tar.xz && \
    cp /ffmpeg/ffmpeg /usr/local/bin/ffmpeg && \
    chmod +x /usr/local/bin/ffmpeg && \
    rm -rf /ffmpeg

# Copy your application requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your FastAPI application code into the image
COPY . /app
WORKDIR /app

# Expose the port your app will run on
EXPOSE 8080

# Command to run your application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
