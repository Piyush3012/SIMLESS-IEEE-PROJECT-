from pymongo import MongoClient

client = MongoClient("mongodb+srv://SIMLESS_DB:simless_project_3@simless.f3nk9hk.mongodb.net/")
db = client["deduplication_db"]
hash_collection = db["hashes"]

def verify_ownership(file_hash):
    stored_hashes = [doc["hash"] for doc in hash_collection.find()]
    return file_hash in stored_hashes
