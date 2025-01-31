from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/lib/mpv/playlists.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configuration
VIDEO_DIR = os.getenv('VIDEO_DIR', '/var/www/html/videos')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}
app.config['UPLOAD_FOLDER'] = VIDEO_DIR

# Database Models
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class PlaylistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    video_path = db.Column(db.String(255), nullable=False)
    position = db.Column(db.Integer, nullable=False)

# Initialize database
with app.app_context():
    db.create_all()

# Initialize MPV controller
mpv_config = {
    'hwdec': 'mmal',
    'vo': 'rpi',
    'state_file': '/var/lib/mpv/state.json'
}
from mpv_controller import MPVController
app.mpv_controller = MPVController(mpv_config)

# Ensure video directory exists
os.makedirs(VIDEO_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video part"}), 400
        
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        app.mpv_controller.add_to_playlist(save_path)
        return jsonify({
            "status": "uploaded",
            "filename": filename,
            "size": os.path.getsize(save_path)
        }), 200
        
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/control', methods=['POST'])
def control_player():
    action = request.json.get('action')
    
    if action == 'play':
        video = request.json.get('video')
        if video:
            app.mpv_controller.play(os.path.join(VIDEO_DIR, video))
            return jsonify({"status": "playing", "video": video})
    elif action == 'pause':
        app.mpv_controller.pause()
        return jsonify({"status": "paused"})
    elif action == 'stop':
        app.mpv_controller.stop()
        return jsonify({"status": "stopped"})
    elif action == 'next':
        app.mpv_controller.next_track()
        return jsonify({"status": "next track"})
    elif action == 'volume':
        app.mpv_controller.set_volume(request.json.get('level'))
        return jsonify({"status": "volume set"})
    
    return jsonify({"error": "Invalid action"}), 400

@app.route('/sync')
def list_videos():
    videos = [f for f in os.listdir(VIDEO_DIR) if os.path.isfile(os.path.join(VIDEO_DIR, f))]
    return jsonify({"videos": videos})

@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_DIR, filename)

@app.route('/playlists', methods=['GET', 'POST'])
def manage_playlists():
    if request.method == 'POST':
        name = request.json.get('name')
        if not name:
            return jsonify({"error": "Playlist name required"}), 400
        
        new_playlist = Playlist(name=name)
        db.session.add(new_playlist)
        db.session.commit()
        return jsonify({
            "id": new_playlist.id,
            "name": new_playlist.name
        }), 201
    
    playlists = Playlist.query.all()
    return jsonify([{"id": p.id, "name": p.name} for p in playlists])

@app.route('/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    items = PlaylistItem.query \
        .filter_by(playlist_id=playlist_id) \
        .order_by(PlaylistItem.position) \
        .all()
    return jsonify({
        "id": playlist.id,
        "name": playlist.name,
        "items": [{"id": item.id, "path": item.video_path} for item in items]
    })

@app.route('/playlist-items/<int:item_id>', methods=['DELETE'])
def remove_playlist_item(item_id):
    item = PlaylistItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"status": "removed"})

@app.route('/playlists/<int:playlist_id>/items', methods=['POST', 'DELETE'])
def manage_playlist_items(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    
    if request.method == 'POST':
        video_path = request.json.get('path')
        if not os.path.exists(video_path):
            return jsonify({"error": "File not found"}), 404
            
        position = PlaylistItem.query.filter_by(playlist_id=playlist_id).count() + 1
        new_item = PlaylistItem(
            playlist_id=playlist_id,
            video_path=video_path,
            position=position
        )
        db.session.add(new_item)
        db.session.commit()
        app.mpv_controller.sync_playlist_to_mpv(playlist_id)
        return jsonify({"status": "added", "position": position}), 201
    
    if request.method == 'DELETE':
        item_id = request.json.get('item_id')
        item = PlaylistItem.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"status": "removed"})

@app.route('/playlist-items/<int:item_id>/position', methods=['PUT'])
def update_playlist_item_position(item_id):
    item = PlaylistItem.query.get_or_404(item_id)
    new_position = request.json.get('position')
    
    if new_position < 1:
        return jsonify({"error": "Invalid position"}), 400

    # Get all items in the playlist
    items = PlaylistItem.query \
        .filter_by(playlist_id=item.playlist_id) \
        .order_by(PlaylistItem.position) \
        .all()

    if new_position > len(items):
        return jsonify({"error": "Position out of range"}), 400

    # Remove item from current position
    items.remove(item)
    # Insert at new position
    items.insert(new_position - 1, item)

    # Update all positions
    for index, item in enumerate(items, start=1):
        item.position = index

    db.session.commit()
    app.mpv_controller.sync_playlist_to_mpv(item.playlist_id)
    return jsonify({"status": "position updated", "new_position": new_position})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)