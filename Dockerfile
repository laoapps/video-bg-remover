# Dockerfile
FROM python:3.8-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ /app

# Expose the app port
EXPOSE 5000

# Start Gunicorn with Flask-SocketIO for WebSocket support
CMD ["gunicorn", "-w", "2", "-k", "eventlet", "-b", "0.0.0.0:34565", "main:app"]
