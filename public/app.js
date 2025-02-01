fetch('http://192.168.0.17:5000/status')
  .then(response => response.json())
  .then(data => {
    document.getElementById('pi-status').textContent = `Pi Status: ${data.status}`;
  });
