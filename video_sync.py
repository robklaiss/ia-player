import os
import requests
import time
from pathlib import Path
import configparser

config = configparser.ConfigParser()
config.read('setup.conf')

SERVER_URL = config['server']['server_url']
LOCAL_VIDEO_DIR = Path(config['directories']['video_storage'])
SYNC_INTERVAL = 300  # 5 minutes

def sync_videos():
    try:
        response = requests.get(f"{SERVER_URL}/sync", timeout=10)
        response.raise_for_status()
        remote_videos = set(response.json().get('videos', []))
        
        local_videos = set([f.name for f in LOCAL_VIDEO_DIR.iterdir() if f.is_file()])
        
        missing_videos = remote_videos - local_videos
        
        for video in missing_videos:
            video_path = LOCAL_VIDEO_DIR / video
            print(f"Downloading {video}...")
            with requests.get(f"{SERVER_URL}/videos/{video}", stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(video_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            print(f"Downloaded {video} ({video_path.stat().st_size >> 20}MB)")
        return True
    except Exception as e:
        print(f"Sync error: {str(e)}")
        return False

if __name__ == '__main__':
    while True:
        if sync_videos():
            print("Sync completed successfully")
        else:
            print("Sync encountered errors")
        time.sleep(SYNC_INTERVAL)
