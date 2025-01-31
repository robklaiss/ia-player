from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.config.update(
    UPLOAD_FOLDER='/var/www/uploads',
    ALLOWED_EXTENSIONS={'mp4', 'mkv', 'webm'},
    MAX_CONTENT_LENGTH=2 * 1024 * 1024 * 1024  # 2GB
)

class VideoManager:
    def __init__(self):
        self.manifest = []
        
    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    def file_checksum(self, filepath):
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def update_manifest(self, filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        self.manifest.append({
            'filename': filename,
            'checksum': self.file_checksum(filepath),
            'size': os.path.getsize(filepath),
            'uploaded': datetime.utcnow().isoformat(),
            'download_url': f'/uploads/{filename}'
        })

video_manager = VideoManager()

@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and video_manager.allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        video_manager.update_manifest(filename)
        return jsonify({'status': 'success', 'filename': filename})

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/manifest')
def get_manifest():
    return jsonify({'videos': video_manager.manifest})

@app.route('/api/playback', methods=['POST'])
def playback_control():
    command = request.json.get('command')
    # Implementation for Pi control would go here
    return jsonify({'status': 'received', 'command': command})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, threaded=True)
