import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/save-recording', methods=['POST'])
def save_recording():
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        recording_id = f'recording_{timestamp}'
        
        # Create recording directory
        recording_dir = os.path.join(current_app.config['RECORDINGS_FOLDER'], recording_id)
        os.makedirs(recording_dir, exist_ok=True)

        # Save video file
        if 'video' in request.files:
            video = request.files['video']
            if video.filename:
                video_path = os.path.join(recording_dir, 'screen_recording.webm')
                video.save(video_path)

        # Save events data
        if 'events' in request.files:
            events = request.files['events']
            if events.filename:
                events_path = os.path.join(recording_dir, 'input_events.json')
                events.save(events_path)

        return jsonify({
            'status': 'success',
            'recordingId': recording_id,
            'timestamp': timestamp
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
