from flask import Flask, jsonify
import os
import json
from functools import lru_cache
import gc

app = Flask(__name__)
CHUNK_FOLDER = "chunks"

FRAMES_PER_FILE = 100 
FRAMES_PER_PAGE = 100  # 1 Request = Exactly 1 File

# Drop cache to maxsize=2 to stay well below Render's 512MB RAM limit
@lru_cache(maxsize=2)
def load_chunk_file(file_index):
    file_path = os.path.join(CHUNK_FOLDER, f"chunk_{file_index}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        data = json.load(f)
        return data

@app.route('/get_chunk/<int:page_index>', methods=['GET'])
def get_chunk(page_index):
    data = load_chunk_file(page_index)
    
    if data is None:
        return jsonify({"error": "End of movie"}), 404
    
    # Strip '#' and pack frames into continuous strings
    compressed_data = []
    for frame in data:
        clean_frame = [color.replace("#", "") for color in frame]
        compressed_data.append("".join(clean_frame))
        
    return jsonify(compressed_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)
