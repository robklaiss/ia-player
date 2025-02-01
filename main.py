#!/usr/bin/env python3
from flask import Flask

app = Flask(__name__)

if __name__ == "__main__":
    app.run()

@app.route('/')
def index():
    return "IA Player Service Running"

@app.route('/status')
def status():
    return {'status': 'active'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
