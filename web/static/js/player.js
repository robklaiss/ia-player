$(document).ready(function() {
    // Load video list
    refreshVideoList();

    // Upload handler
    $('#uploadForm').submit(function(e) {
        e.preventDefault();
        const formData = new FormData();
        formData.append('video', $('#videoFile')[0].files[0]);

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                $('#videoFile').val('');
                refreshVideoList();
            }
        });
    });

    // Player controls
    $('#playBtn').click(() => sendCommand('play'));
    $('#pauseBtn').click(() => sendCommand('pause'));
    $('#stopBtn').click(() => sendCommand('stop'));
    $('#nextBtn').click(() => sendCommand('next'));
    
    $('#volumeSlider').on('input', function() {
        sendCommand('volume', { level: $(this).val() });
    });

    function refreshVideoList() {
        $.get('/sync', function(data) {
            const videos = data.videos;
            $('#videoList').empty();
            videos.forEach(video => {
                $('#videoList').append(
                    `<div class="list-group-item video-item" data-video="${video}">
                        ${video}
                        <button class="btn btn-sm btn-primary float-end play-btn">Play</button>
                    </div>`
                );
            });

            $('.play-btn').click(function() {
                const video = $(this).closest('.video-item').data('video');
                sendCommand('play', { video: video });
            });
        });
    }

    function sendCommand(action, data = {}) {
        $.post('/control', {
            action: action,
            ...data
        }, function(response) {
            console.log(response);
        });
    }
// In /web/static/js/player.js around line 61
// Playlist management functions
    async function refreshPlaylists() {
      try {
        const [playlistsRes, videosRes] = await Promise.all([
          fetch('/playlists'),
          fetch('/sync')
        ]);
        
        const playlists = await playlistsRes.json();
        const videos = (await videosRes.json()).videos;
        
        const container = document.querySelector('.playlist-list');
        container.innerHTML = await Promise.all(playlists.map(async p => {
          const res = await fetch(`/playlists/${p.id}`);
          const playlist = await res.json();
          return `
            <div class="playlist-item" data-id="${p.id}">
              <h3>${p.name}</h3>
              <div class="playlist-controls">
                <select class="video-select">
                  ${videos.map(v => `<option value="${v}">${v}</option>`).join('')}
                </select>
                <button onclick="addVideoToPlaylist(${p.id}, this)">Add Video</button>
                <button onclick="deletePlaylist(${p.id})">Delete Playlist</button>
              </div>
              <div id="playlist-container" class="playlist-videos">
                ${playlist.items.map(i => `
                  <div class="playlist-video-item" data-item-id="${i.id}">
                    <span>${i.path.split('/').pop()}</span>
                    <button class="move-up-btn" data-item-id="${i.id}">↑</button>
                    <button class="move-down-btn" data-item-id="${i.id}">↓</button>
                    <button onclick="removeVideoFromPlaylist(${i.id})">×</button>
                    <span class="drag-handle">≡</span>
                  </div>
                `).join('')}
              </div>
            </div>
          `;
        }));
        playlists.forEach(p => initializeSortable(p.id));
      } catch (error) {
        console.error('Error refreshing playlists:', error);
      }
    }

    async function createPlaylist() {
      const name = document.getElementById('new-playlist-name').value;
      await fetch('/playlists', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name })
      });
      refreshPlaylists();
    }

    async function deletePlaylist(playlistId) {
      await fetch(`/playlists/${playlistId}`, { method: 'DELETE' });
      refreshPlaylists();
    }
// In /web/static/js/player.js after deletePlaylist
async function removeVideoFromPlaylist(itemId) {
  try {
    const response = await fetch(`/playlist-items/${itemId}`, { 
      method: 'DELETE' 
    });
    if (!response.ok) throw new Error('Removal failed');
    refreshPlaylists();
  } catch (error) {
    alert('Failed to remove video: ' + error.message);
  }
}
    async function addVideoToPlaylist(playlistId, button) {
      const videoPath = button.previousElementSibling.value;
      const response = await fetch(`/playlists/${playlistId}/items`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ path: videoPath })
      });
      
      if (response.ok) {
        refreshPlaylists();
      } else {
        alert('Failed to add video to playlist');
      }
    }

    function initializeSortable(playlistId) {
        new Sortable(document.querySelector(`[data-id="${playlistId}"] .playlist-videos`), {
            animation: 150,
            handle: '.drag-handle',
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            onUpdate: async (evt) => {
                const itemId = evt.item.dataset.itemId;
                const newPosition = evt.newIndex + 1;
                
                try {
                    const response = await fetch(`/playlist-items/${itemId}/position`, {
                        method: 'PUT',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({position: newPosition})
                    });
                    
                    if (!response.ok) throw new Error('Failed to update position');
                    
                    evt.item.classList.add('update-confirmed');
                    setTimeout(() => evt.item.classList.remove('update-confirmed'), 500);
                    
                } catch (error) {
                    console.error('Drag position update failed:', error);
                    evt.item.parentNode.insertBefore(evt.item, evt.item.parentNode.children[evt.oldIndex]);
                }
            }
        });
    }

    function refreshPlaylist(playlistId) {
        fetch(`/playlists/${playlistId}`)
            .then(response => response.json())
            .then(playlist => {
                renderPlaylist(playlist);
                initializeSortable(playlistId);
            });
    }

    function handlePositionUpdate(itemId, direction) {
        const itemElement = document.querySelector(`[data-item-id="${itemId}"]`).closest('.playlist-item');
        const currentPosition = Array.from(itemElement.parentNode.children).indexOf(itemElement) + 1;
        const newPosition = direction === 'up' ? currentPosition - 1 : currentPosition + 1;

        fetch(`/playlist-items/${itemId}/position`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({position: newPosition})
        })
        .then(response => {
            if (response.ok) {
                const playlistContainer = itemElement.parentNode;
                if (direction === 'up') {
                    playlistContainer.insertBefore(itemElement, itemElement.previousElementSibling);
                } else {
                    playlistContainer.insertBefore(itemElement.nextElementSibling, itemElement);
                }
            }
        })
        .catch(error => console.error('Error updating position:', error));
    }

    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('move-up-btn')) {
            handlePositionUpdate(event.target.dataset.itemId, 'up');
        }
        if (event.target.classList.contains('move-down-btn')) {
            handlePositionUpdate(event.target.dataset.itemId, 'down');
        }
    });

    // Initialize playlists on load
    window.addEventListener('load', () => {
      refreshPlaylists();
    });
});