from flask import Flask, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

VIDEO_DIR = os.getenv('VIDEO_DIR', '/var/www/html/videos')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}

os.makedirs(VIDEO_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video part"}), 400
        
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(VIDEO_DIR, filename)
        file.save(save_path)
        return jsonify({
            "status": "uploaded",
            "filename": filename,
            "size": os.path.getsize(save_path)
        }), 200
        
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/sync')
def list_videos():
    videos = [f for f in os.listdir(VIDEO_DIR) if os.path.isfile(os.path.join(VIDEO_DIR, f))]
    return jsonify({"videos": videos})

@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_DIR, filename)

    # In /web/app.py after playlist items routes
    @app.route('/playlist-items/<int:item_id>', methods=['DELETE'])
    def remove_playlist_item(item_id):
        item = PlaylistItem.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"status": "removed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
