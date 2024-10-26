# app/main.py
import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from background_removal import load_model, remove_background

app = Flask(__name__)
socketio = SocketIO(app)
model = load_model()

# Limits
MAX_VIDEO_DURATION = 10  # seconds for file processing
MAX_FRAME_DURATION = 0.5  # seconds for each real-time frame

# HTTP endpoint for file processing
@app.route('/process_file', methods=['POST'])
def process_file():
    file = request.files.get('file')
    background_color = request.form.get('background_color', '#FFFFFF')  # Default to white if not provided

    if not file:
        return jsonify({'error': 'No file provided'}), 400

    # Save input file
    input_path = os.path.join('input', 'input_video.mp4')
    file.save(input_path)

    # Process video file
    output_path = os.path.join('output', 'output_video.mp4')
    if process_video(input_path, output_path, background_color=background_color, max_duration=MAX_VIDEO_DURATION):
        return send_from_directory(directory='output', filename='output_video.mp4')
    else:
        return jsonify({'error': 'Video too long. Max duration is 10 seconds.'}), 400

def process_video(input_path, output_path, background_color="#FFFFFF", max_duration=MAX_VIDEO_DURATION):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps

    # Check if video duration exceeds the limit
    if duration > max_duration:
        cap.release()
        return False  # Video too long

    # Define codec and create VideoWriter for output
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame for file-based request with background color
        processed_frame = remove_background(frame, model, for_realtime=False, background_color=background_color)
        out.write(processed_frame)

    cap.release()
    out.release()
    return True

# WebSocket endpoint for real-time frame processing
@socketio.on('process_frame')
def handle_process_frame(data):
    frame_data = data.get('frame')
    width, height = data.get('width'), data.get('height')
    
    # Decode and reshape the frame
    frame = np.frombuffer(frame_data, np.uint8).reshape((height, width, 3))
    
    # Process the frame for real-time request without a background color
    processed_frame = remove_background(frame, model, for_realtime=True)

    # Encode and send the processed frame back to the client
    _, buffer = cv2.imencode('.jpg', processed_frame)
    emit('processed_frame', buffer.tobytes())

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT') or 34565))
