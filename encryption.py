import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import boto3

s3 = boto3.client("s3")
BUCKET_NAME = "simless-bucket"

# Simulated Key Storage (Use a secure method like a database in production)
KEY_STORAGE = {}

def get_encryption_key(filename):
    """Retrieve encryption key for a file, or generate and store a new one."""
    if filename in KEY_STORAGE:
        return KEY_STORAGE[filename]
    
    key = os.urandom(32)  # AES-256 requires 32-byte key
    KEY_STORAGE[filename] = key  # Store securely in a DB or environment
    return key

def encrypt_file(file_path, key):
    """Encrypts a file using AES with a random IV."""
    with open(file_path, "rb") as f:
        plaintext = f.read()

    # Generate a secure random IV
    iv = os.urandom(16)  # AES block size is 16 bytes

    # Add padding (AES requires input to be a multiple of block size)
    padder = padding.PKCS7(128).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    # Prepend IV to the encrypted data (needed for decryption)
    encrypted_blob = iv + ciphertext  

    # Encode in Base64 before uploading to S3
    return base64.b64encode(encrypted_blob)

def upload_to_s3(file_name, encrypted_data):
    """Uploads encrypted data to S3."""
    s3.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=encrypted_data)

def delete_from_s3(file_name):
    """Deletes a file from S3 bucket."""
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=file_name)
        print(f"File {file_name} deleted from S3 successfully.")
        return True
    except Exception as e:
        print(f"Error deleting {file_name} from S3: {e}")
        return False

def download_from_s3(file_name):
    """Downloads a file from S3 and returns the encrypted content."""
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=file_name)
        encrypted_data = response["Body"].read()
        return encrypted_data
    except Exception as e:
        print(f"Error downloading {file_name} from S3: {e}")
        return None
