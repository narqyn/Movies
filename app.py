from flask import Flask, jsonify
import os
import json

app = Flask(__name__)
CHUNK_FOLDER = "chunks"

FRAMES_PER_FILE = 100 
FRAMES_PER_PAGE = 5  # Keeps payload tiny to bypass Roblox limits

# FIX 2: In-Memory Cache to prevent disk-read bottleneck!
chunk_cache = {}

def get_file_data(file_index):
    # If we already read this file, grab it from RAM instantly
    if file_index in chunk_cache:
        return chunk_cache[file_index]
    
    # If not, read it from disk and save it to RAM
    file_path = os.path.join(CHUNK_FOLDER, f"chunk_{file_index}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            chunk_cache[file_index] = data
            return data
    return None

@app.route('/get_chunk/<int:page_index>', methods=['GET'])
def get_chunk(page_index):
    zero_based_page = page_index - 1
    start_frame = zero_based_page * FRAMES_PER_PAGE
    
    file_index = (start_frame // FRAMES_PER_FILE) + 1
    local_start = start_frame % FRAMES_PER_FILE
    
    data = get_file_data(file_index)
    
    if data:
        frames_needed = FRAMES_PER_PAGE
        available_in_file = len(data) - local_start
        
        if frames_needed <= available_in_file:
            sliced_data = data[local_start : local_start + frames_needed]
        else:
            sliced_data = data[local_start:]
            frames_still_needed = frames_needed - len(sliced_data)
            
            data2 = get_file_data(file_index + 1)
            if data2:
                sliced_data.extend(data2[:frames_still_needed])
        
        # Super-fast string compression
        compressed_data = []
        for frame in sliced_data:
            clean_frame = [color.replace("#", "") for color in frame]
            compressed_data.append("".join(clean_frame))
            
        return jsonify(compressed_data)
    else:
        return jsonify({"error": "End of movie"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)
