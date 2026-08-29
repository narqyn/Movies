from flask import Flask, jsonify
import os
import json

app = Flask(__name__)
CHUNK_FOLDER = "chunks"

@app.route('/get_chunk/<int:chunk_index>', methods=['GET'])
def get_chunk(chunk_index):
    file_path = os.path.join(CHUNK_FOLDER, f"chunk_{chunk_index}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "Chunk not found"}), 404

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)
