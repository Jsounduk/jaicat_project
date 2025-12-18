from PIL import Image
import imagehash

def check_duplicate(path1, path2, threshold=5):
    """
    Check if two images are visually similar using average hash.
    Return True if the hamming distance is below the threshold.
    """
    try:
        hash1 = imagehash.average_hash(Image.open(path1))
        hash2 = imagehash.average_hash(Image.open(path2))
        return hash1 - hash2 < threshold
    except Exception as e:
        print(f"⚠️ Duplicate check failed: {e}")
        return False
