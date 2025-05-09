from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import base64
import encryption
import boto3

s3 = boto3.client("s3")
BUCKET_NAME = "simless-bucket"

def get_encrypted_file(file_name):
    """Fetches the encrypted file from S3."""
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=file_name)
        encrypted_data = response["Body"].read()
        return encrypted_data
    except Exception as e:
        print(f"Error fetching file from S3: {e}")
        return None

def get_decryption_key(filename):
    """Retrieves the stored encryption key."""
    return encryption.KEY_STORAGE.get(filename)

def decrypt_file(encrypted_data, key):
    """Decrypts an encrypted file using AES."""
    encrypted_data = base64.b64decode(encrypted_data)

    # Extract IV from the encrypted file
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv))
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

    # Remove padding
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()

    return decrypted_data
