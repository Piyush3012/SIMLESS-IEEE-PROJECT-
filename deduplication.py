def hamming_distance(hash1, hash2):
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

def is_duplicate(new_hash, stored_hashes, threshold=5):
    for existing_hash in stored_hashes:
        if hamming_distance(new_hash, existing_hash) <= threshold:
            return True
    return False