# app/background_removal.py
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import DeepLabV3

def load_model():
    """Load and return the DeepLabV3 model for background removal."""
    model = DeepLabV3(weights='pascal_voc', input_shape=(512, 512, 3), include_top=False)
    return model

def hex_to_rgb(hex_color):
    """Convert hex color code to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def remove_background(frame, model, for_realtime=False, background_color="#FFFFFF"):
    """
    Remove the background from the frame.

    Parameters:
    - frame: The input frame to process.
    - model: The background removal model.
    - for_realtime: If True, keep only the masked foreground (no background).
    - background_color: Hex color code for the background, default is white.

    Returns:
    - result: Frame with background removed or replaced.
    """
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
    
    # If real-time, return only the masked foreground without a background
    if for_realtime:
        result = cv2.bitwise_and(frame, frame, mask=binary_mask)
        return result
    
    # File-based processing: Create a solid color background
    bg_color_rgb = hex_to_rgb(background_color) if background_color else (255, 255, 255)
    background_img = np.full((original_height, original_width, 3), bg_color_rgb, dtype=np.uint8)
    
    # Apply mask to create foreground and combine with background
    fg_mask = cv2.bitwise_and(frame, frame, mask=binary_mask)
    bg_mask = cv2.bitwise_and(background_img, background_img, mask=cv2.bitwise_not(binary_mask))
    
    # Combine foreground and background
    result = cv2.add(fg_mask, bg_mask)
    return result
