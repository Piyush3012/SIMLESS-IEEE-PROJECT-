from pymongo import MongoClient
import os
from dotenv import load_dotenv


load_dotenv()  # Load variables from .env
mongo_uri = os.getenv("MONGO_URI")  # Fetch the value
client = MongoClient(mongo_uri)
db = client["deduplication_db"]
hash_collection = db["hashes"]

def verify_ownership(file_hash):
    stored_hashes = [doc["hash"] for doc in hash_collection.find()]
    return file_hash in stored_hashes
