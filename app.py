from flask import Flask, jsonify
import os
import json
from functools import lru_cache

app = Flask(__name__)
CHUNK_FOLDER = "chunks"

FRAMES_PER_FILE = 100 
FRAMES_PER_PAGE = 90  # 90 frames = 3 solid seconds of video per request

# FIX 1: Keep the last 8 chunk files directly in RAM. Zero disk lag!
@lru_cache(maxsize=8)
def load_chunk_file(file_index):
    file_path = os.path.join(CHUNK_FOLDER, f"chunk_{file_index}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        return json.load(f)

@app.route('/get_chunk/<int:page_index>', methods=['GET'])
def get_chunk(page_index):
    zero_based_page = page_index - 1
    start_frame = zero_based_page * FRAMES_PER_PAGE
    
    file_index = (start_frame // FRAMES_PER_FILE) + 1
    local_start = start_frame % FRAMES_PER_FILE
    
    data = load_chunk_file(file_index)
    if data is None:
        return jsonify({"error": "End of movie"}), 404
        
    frames_needed = FRAMES_PER_PAGE
    sliced_data = data[local_start : local_start + frames_needed]
    
    if len(sliced_data) < frames_needed:
        next_data = load_chunk_file(file_index + 1)
        if next_data:
            sliced_data = sliced_data + next_data[: frames_needed - len(sliced_data)]
    
    # FIX 2: Pack 8,160 items into 1 string per frame to destroy JSON bloat
    compressed_data = []
    for frame in sliced_data:
        clean_frame = [color.replace("#", "") for color in frame]
        compressed_data.append("".join(clean_frame))
        
    return jsonify(compressed_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)
