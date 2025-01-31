import os
import requests
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv('SYNC_SERVER_URL')
API_KEY = os.getenv('API_KEY')
VIDEO_DIR = '/home/pi/videos/synced'

class VideoSyncer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {API_KEY}'})

    def get_remote_manifest(self):
        try:
            response = self.session.get(f'{SERVER_URL}/api/manifest')
            return response.json()['videos']
        except Exception as e:
            print(f'Error fetching manifest: {e}')
            return []

    def get_local_checksums(self):
        return {
            fname: hashlib.md5(open(os.path.join(VIDEO_DIR, fname), 'rb').read()).hexdigest()
            for fname in os.listdir(VIDEO_DIR)
            if fname.endswith('.mp4')
        }

    def sync_videos(self):
        local_checksums = self.get_local_checksums()
        remote_manifest = self.get_remote_manifest()

        for video in remote_manifest:
            local_path = os.path.join(VIDEO_DIR, video['filename'])
            
            if not os.path.exists(local_path) or \
               local_checksums.get(video['filename']) != video['checksum']:
                
                print(f'Downloading {video['filename']}')
                self.download_video(video['download_url'], local_path)

    def download_video(self, url, path):
        with self.session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

if __name__ == '__main__':
    syncer = VideoSyncer()
    while True:
        syncer.sync_videos()
        time.sleep(300)  # Check every 5 minutes
