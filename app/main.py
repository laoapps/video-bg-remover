# app/main.py
from flask import Flask, request, jsonify, send_from_directory
import os
import cv2
import time
import threading
from datetime import datetime, timedelta
from background_removal import load_model, remove_background

app = Flask(__name__)
model = load_model()
output_dir = 'output/frames'
os.makedirs(output_dir, exist_ok=True)

# Start a cleanup thread to delete old files every 5 minutes
def start_cleanup_task():
    def cleanup_old_files():
        while True:
            # Check for files older than 5 minutes
            now = datetime.now()
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                if os.path.isfile(file_path):
                    file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if now - file_modified_time > timedelta(minutes=5):
                        os.remove(file_path)
            time.sleep(300)  # Wait 5 minutes before checking again

    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
    cleanup_thread.start()

# Call the cleanup function to start it when the app runs
start_cleanup_task()

# Endpoint for file processing with optional transparent background
@app.route('/process_file', methods=['POST'])
def process_file():
    file = request.files.get('file')
    transparent = request.form.get('transparent', 'false').lower() == 'true'

    if not file:
        return jsonify({'error': 'No file provided'}), 400

    # Save input file (expects MOV format for compatibility with prores_4444 codec)
    input_path = os.path.join('input', 'input_video.mov')
    file.save(input_path)

    # Process video file frame-by-frame for transparency
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        # Remove background with transparency if requested
        processed_frame = remove_background(frame, model, transparent=transparent)

        # Save as PNG with transparency (if applicable)
        frame_output_path = os.path.join(output_dir, f"frame_{i:04d}.png")
        cv2.imwrite(frame_output_path, processed_frame)

    cap.release()
    
    # Convert PNG sequence to MOV format with transparency
    output_video_path = os.path.join('output', 'output_video_with_transparency.mov')
    os.system(f"ffmpeg -framerate {fps} -i {output_dir}/frame_%04d.png -c:v prores_ks -profile:v 4 {output_video_path}")

    # Return the MOV file to the client
    return send_from_directory(directory='output', filename='output_video_with_transparency.mov')
