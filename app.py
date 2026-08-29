from flask import Flask, jsonify
import os
import json

app = Flask(__name__)
CHUNK_FOLDER = "chunks"

FRAMES_PER_FILE = 100  # Keep this 100 since your physical GitHub files have 100 frames!
FRAMES_PER_PAGE = 15   # The safe limit Roblox can handle per request

@app.route('/get_chunk/<int:page_index>', methods=['GET'])
def get_chunk(page_index):
    # Calculate the global starting frame based on what Roblox asked for
    zero_based_page = page_index - 1
    start_frame = zero_based_page * FRAMES_PER_PAGE
    
    # Figure out which physical JSON file holds this frame
    file_index = (start_frame // FRAMES_PER_FILE) + 1
    local_start = start_frame % FRAMES_PER_FILE
    
    sliced_data = []
    
    file_path = os.path.join(CHUNK_FOLDER, f"chunk_{file_index}.json")
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            
        frames_needed = FRAMES_PER_PAGE
        available_in_file = len(data) - local_start
        
        # If the requested slice fits entirely inside the current file
        if frames_needed <= available_in_file:
            sliced_data = data[local_start : local_start + frames_needed]
        else:
            # The slice crosses the boundary between two files!
            # Grab what's left in the first file...
            sliced_data = data[local_start:]
            frames_still_needed = frames_needed - len(sliced_data)
            
            # ...and stitch it together with the start of the next file
            next_file_path = os.path.join(CHUNK_FOLDER, f"chunk_{file_index + 1}.json")
            if os.path.exists(next_file_path):
                with open(next_file_path, "r") as f2:
                    data2 = json.load(f2)
                sliced_data.extend(data2[:frames_still_needed])
                
        return jsonify(sliced_data)
    else:
        return jsonify({"error": "End of movie"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)
