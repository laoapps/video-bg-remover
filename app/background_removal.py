# app/background_removal.py
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import DeepLabV3

def load_model():
    model = DeepLabV3(weights='pascal_voc', input_shape=(512, 512, 3), include_top=False)
    return model

def hex_to_rgb(hex_color):
    """Convert hex color code to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def remove_background(frame, model, background_color="#FFFFFF"):
    # Preserve original frame dimensions
    original_height, original_width = frame.shape[:2]
    
    # Resize frame to model input size for processing
    resized_frame = cv2.resize(frame, (512, 512))
    normalized_frame = np.expand_dims(resized_frame / 255.0, axis=0)
    
    # Perform prediction to get the segmentation mask
    mask = model.predict(normalized_frame)[0]
    
    # Resize the mask back to the original frame size
    mask = cv2.resize(mask, (original_width, original_height))
    
    # Create binary mask
    binary_mask = (mask[:, :, 0] > 0.5).astype(np.uint8) * 255
    
    # Prepare the background color as an image
    if background_color:
        bg_color_rgb = hex_to_rgb(background_color)
    else:
        bg_color_rgb = (255, 255, 255)  # Default to white
    
    # Create a solid color background image of the same size as the frame
    background_img = np.full((original_height, original_width, 3), bg_color_rgb, dtype=np.uint8)
    
    # Apply the mask to create the final image with the background color
    fg_mask = cv2.bitwise_and(frame, frame, mask=binary_mask)
    bg_mask = cv2.bitwise_and(background_img, background_img, mask=cv2.bitwise_not(binary_mask))
    
    result = cv2.add(fg_mask, bg_mask)
    return result
