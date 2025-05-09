import imagehash
from PIL import Image
import cv2
import numpy as np
import hashlib
import re

def generate_phash(file_path):
    image = Image.open(file_path)
    phash = imagehash.phash(image)
    return str(phash)

def extract_keyframes(video_path):
    cap = cv2.VideoCapture(video_path)
    keyframes = []
    frame_count = 0
    prev_frame = None
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Save the first frame or if a significant change occurs
        if prev_frame is None or cv2.norm(gray, prev_frame) > 30:
            keyframes.append(gray)
        
        prev_frame = gray
        frame_count += 1
    
    cap.release()
    return keyframes

def generate_video_hash(keyframes):
    
    hashes = []
    
    for frame in keyframes:
        # Convert frame to PIL Image
        pil_img = Image.fromarray(frame)

        # Compute perceptual hash (pHash)
        frame_hash = str(imagehash.phash(pil_img))
        hashes.append(frame_hash)
    
    # Combine all frame hashes into a single representative hash
    if hashes:
        combined_hash = "".join(hashes)
        return combined_hash[:16]  # Truncate to 16 characters for efficiency
    else:
        return None  # No keyframes found, return None
    

def generate_text_hash(text):
    
    # Preprocess text (remove punctuation, convert to lowercase)
    words = re.findall(r'\w+', text.lower())

    # Hash individual words and create a bit vector
    hash_vector = [0] * 128  # 128-bit SimHash
    for word in words:
        word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)  # Convert word to hash
        for i in range(128):
            if word_hash & (1 << i):  # Check each bit
                hash_vector[i] += 1
            else:
                hash_vector[i] -= 1

    # Generate final SimHash
    simhash = ''.join(['1' if x > 0 else '0' for x in hash_vector])
    return simhash
