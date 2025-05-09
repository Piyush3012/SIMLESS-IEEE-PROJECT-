# 📘 SIMLESS(IEEE PROJECT)

**SIMLESS** is a secure file upload system that automatically encrypts uploaded files using Fuzzy Ownership Logic and stores them on the server and cloud only if they are unique. It prevents redundant uploads through deduplication detection while ensuring confidentiality through AES-based encryption. Built with a MERN stack and Python backend integration.

---

## 🧑‍🤝‍🧑 Contributors

Thanks to the following contributors for their efforts in building this project:

- [@maithilmishra](https://github.com/maithilmishra)
- [@idPriyanshu](https://github.com/idPriyanshu)

---

## 🔍 Project Overview

This project is designed to:

User uploads a file via a web interface.

The backend:

1. Generates a perceptual hash of the file.
2. Checks if a similar file already exists (deduplication).
3. If unique, encrypts the file using AES + Fuzzy Ownership Logic.
4. Uploads it securely to the cloud.
5. Duplicate files are not re-uploaded, saving bandwidth and storage.

---

## 🛠️ Features
Website Crawling: Extract HTML code, methods (GET, POST, etc.), and potential vulnerable endpoints.
 
🔐 Automatically encrypts uploaded files using AES and Fuzzy Ownership Logic
🔍 Detects and prevents duplicate file uploads via perceptual hashing
☁️ Stores only unique, encrypted files on cloud (e.g., Cloudinary)
⚡ Clean and responsive UI built with React, Vite, and Tailwind CSS
🔄 MERN stack integrated with Python backend for encryption and deduplication logic


---

## ⚙️ Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/SIMLESS-IEEE-PROJECT-.git
    
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Run the web interface

1. Run the backend:

    ```bash
    python app.py
    
    ```
2. Run the frontend

    ```bash
    cd frontend 
    npm run start 
    
    ```

## Future Enhancements

1. Support for Cross-Platform Media Deduplication
Extend the system to handle deduplication across multiple platforms or cloud providers (e.g., AWS, Google Drive, Dropbox), enabling unified media storage optimization in hybrid cloud environments.

2. Integration of Machine Learning for Similarity Detection
Enhance the similarity-preserving hash function with deep learning models (e.g., CNNs for image/video features) to improve detection accuracy for more complex or edited media.

3. Real-Time Duplicate Detection and Alerts
Add real-time deduplication and user notification mechanisms so that as soon as a similar file is detected during upload, the user is alerted with options to proceed, skip, or review similar content.

**"This project demonstrates a secure, privacy-preserving deduplication system for similar media files using the MERN stack and Python, offering a scalable solution for efficient and intelligent cloud media storage."**



