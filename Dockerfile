# Dockerfile
FROM python:3.8-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ /app

# Expose the app port
EXPOSE 5000

# Define the entry point for the app
CMD ["python", "main.py"]
