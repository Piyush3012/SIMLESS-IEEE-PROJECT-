from flask import Flask, request, jsonify,send_file
from flask_cors import CORS
import os
from pymongo import MongoClient
import hashing
import deduplication
import encryption
import decryption
# import hashlib

app = Flask(__name__)
CORS(app)



# Database setup
client = MongoClient("mongodb+srv://SIMLESS_DB:simless_project_3@simless.f3nk9hk.mongodb.net/?retryWrites=true&tls=true")
db = client["deduplication_db"]
hash_collection = db["hashes"]

# Ensure the upload directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        print("Upload request received")

        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file_extension = file.filename.split(".")[-1].lower()
        file.save(file_path)

        # **If it's a video, process keyframes**
        if file_extension in ["mp4", "avi", "mov", "mkv"]:
            keyframes = hashing.extract_keyframes(file_path)
            new_hash = hashing.generate_video_hash(keyframes)  # Generate hash from keyframes
        elif file_extension in ["txt", "csv", "log", "json", "xml"]:
            new_hash = hashing.generate_text_hash(file_path)  # SimHash for text
        else:
            new_hash = hashing.generate_phash(file_path)  # Regular file hashing

        # Fetch stored hashes from DB
        stored_hashes = [entry["hash"] for entry in hash_collection.find({}, {"hash": 1})]

        # Check for duplicates
        if deduplication.is_duplicate(new_hash, stored_hashes):
         
            return jsonify({"message": "Duplicate file detected based on hash similarity!"}), 409

        # Store hash in the database
        hash_collection.insert_one({"hash": new_hash, "filename": file.filename})

        # Encrypt and upload file to S3
        encryption_key = encryption.get_encryption_key(file.filename)
        encrypted_data = encryption.encrypt_file(file_path, encryption_key)
        encryption.upload_to_s3(file.filename, encrypted_data)

        return jsonify({"message": "File uploaded successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/verify", methods=["POST"])
def verify_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file_extension = file.filename.split(".")[-1].lower()
        
        # Save the file temporarily for verification
        file.save(file_path)

        # Determine the hashing method based on file type
        if file_extension in ["mp4", "avi", "mov", "mkv"]:
            keyframes = hashing.extract_keyframes(file_path)
            file_hash = hashing.generate_video_hash(keyframes)  # Hash from keyframes
        elif file_extension in ["txt", "csv", "log", "json", "xml"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                file_content = f.read()
            file_hash = hashing.generate_text_hash(file_content)  # Hash for text files
        else:
            file_hash = hashing.generate_phash(file_path)  # Default perceptual hash

        # Check if the generated hash exists in the database
        file_entry = hash_collection.find_one({"hash": file_hash})

        # **Delete the file after verification is completed**
        if file_entry:
            return jsonify({"message": "Ownership verified."}), 200
        else:
            os.remove(file_path)  # ❌ Delete only if verification fails
            return jsonify({"message": "Ownership not verified."}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/decrypt", methods=["POST"])
def decrypt_request():
    try:
        file_name = request.json.get("filename")
        if not file_name:
            return jsonify({"error": "Filename not provided"}), 400

        encrypted_data = decryption.get_encrypted_file(file_name)
        if not encrypted_data:
            return jsonify({"error": "Encrypted file not found"}), 404

        key = decryption.get_decryption_key(file_name)
        if not key:
            return jsonify({"error": "Decryption key not found"}), 404

        decrypted_content = decryption.decrypt_file(encrypted_data, key)

        return jsonify({"message": "File decrypted successfully!", "content": decrypted_content.decode(errors='ignore')})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/delete", methods=["POST"])
def delete_file():
    try:
        filename = request.json.get("filename")

        if not filename:
            return jsonify({"error": "Filename not provided"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Find the file in MongoDB
        file_entry = hash_collection.find_one({"filename": filename})

        if not file_entry:
            return jsonify({"message": "File record not found in database!"}), 404

        # Remove file from local storage if exists
        if os.path.exists(file_path):
            os.remove(file_path)

        # Remove file from S3
        deleted_from_s3 = encryption.delete_from_s3(filename)  # Add this function

        if not deleted_from_s3:
            return jsonify({"error": "Failed to delete file from cloud storage!"}), 500

        # Remove the file entry from the database
        hash_collection.delete_one({"filename": filename})

        return jsonify({"message": "File deleted successfully from local storage, cloud, and database!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route("/download", methods=["POST"])
def download_file():
    try:
        filename = request.json.get("filename")

        if not filename:
            return jsonify({"error": "Filename not provided"}), 400

        # Fetch encrypted data from S3
        encrypted_data = encryption.download_from_s3(filename)
        if not encrypted_data:
            return jsonify({"error": "File not found in cloud storage"}), 404

        # Decrypt the file
        key = decryption.get_decryption_key(filename)
        decrypted_content = decryption.decrypt_file(encrypted_data, key)

        # Save decrypted file temporarily
        temp_file_path = f"temp/{filename}"
        with open(temp_file_path, "wb") as f:
            f.write(decrypted_content)

        # Send the file for download
        return send_file(temp_file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/keys", methods=["GET"])
def get_keys():
    """Returns the stored encryption keys (FOR DEBUGGING ONLY)"""
    return jsonify({"keys": {k: v.hex() for k, v in encryption.KEY_STORAGE.items()}})


@app.route("/list-files", methods=["GET"])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify({"files": files})


if __name__ == "__main__":
    app.run(debug=True)
