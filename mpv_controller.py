from mpv import MPV
from flask import current_app
import os
import logging

class MPVController:
    def __init__(self):
        """Initialize MPV player with Raspberry Pi optimized settings"""
        self.mpv = MPV(
            hwdec='rpi',  # Raspberry Pi hardware decoding
            vo='rpi',     # Raspberry Pi video output
            input_default_bindings=True,
            input_vo_keyboard=True,
            osc=True,
            loglevel='warn'
        )
        self.logger = logging.getLogger(__name__)
        
        # Configure database path from Flask app context
        self.db_path = os.path.join(
            current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''),
            'playlists.db'
        )

    def sync_playlist_to_mpv(self, playlist_id):
        """Sync database playlist to MPV player"""
        try:
            from web.app import PlaylistItem  # Local import to avoid circular dependency
            
            items = PlaylistItem.query.filter_by(playlist_id=playlist_id)\
                                    .order_by(PlaylistItem.position)\
                                    .all()
            
            # Preserve current playback state
            current_pos = self.mpv.get_property('playlist-pos-1') or 0
            pause_state = self.mpv.get_property('pause')
            
            # Clear and reload playlist
            self.mpv.command('playlist-clear')
            for item in items:
                if os.path.exists(item.video_path):
                    self.mpv.command('loadfile', item.video_path, 'append')
                else:
                    self.logger.error(f"File not found: {item.video_path}")
            
            # Restore playback state
            if items and current_pos < len(items):
                self.mpv.command('playlist-play-index', current_pos)
                if pause_state:
                    self.mpv.command('set', 'pause', 'yes')
            
            return True
        except Exception as e:
            self.logger.error(f"Playlist sync failed: {str(e)}")
            return False

    def play(self):
        self.mpv.command('set', 'pause', 'no')
    
    def pause(self):
        self.mpv.command('set', 'pause', 'yes')
    
    def stop(self):
        self.mpv.command('stop')
    
    def next(self):
        self.mpv.command('playlist-next')
    
    @property
    def status(self):
        return {
            'playing': not self.mpv.get_property('pause'),
            'position': self.mpv.get_property('time-pos'),
            'duration': self.mpv.get_property('duration'),
            'current_file': self.mpv.get_property('path')
        }

if __name__ == "__main__":
    # Raspberry Pi specific initialization
    controller = MPVController()
    try:
        print("MPV Player Service Started. Press Ctrl+C to exit.")
        controller.mpv.wait_for_playback()
    except KeyboardInterrupt:
        print("\nShutting down MPV controller...")
        controller.mpv.terminate()