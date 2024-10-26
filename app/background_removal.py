# app/background_removal.py
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import DeepLabV3

def load_model():
    model = DeepLabV3(weights='pascal_voc', input_shape=(512, 512, 3), include_top=False)
    return model

def remove_background(frame, model):
    resized_frame = cv2.resize(frame, (512, 512))
    normalized_frame = np.expand_dims(resized_frame / 255.0, axis=0)
    
    mask = model.predict(normalized_frame)[0]
    mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

    binary_mask = (mask[:, :, 0] > 0.5).astype(np.uint8) * 255
    result = cv2.bitwise_and(frame, frame, mask=binary_mask)
    return result
