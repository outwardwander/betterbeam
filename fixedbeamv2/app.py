from flask import Flask, request, jsonify, render_template
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Your API key and base URL for the info-beamer API
API_KEY = '5e275aeda638fe05724c30531e0ed526'
BASE_URL = 'https://info-beamer.com/api/v1/'

# Folder to save uploaded assets (ensure this folder exists)
UPLOAD_FOLDER = 'uploaded_assets'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper function to get headers for authentication
def get_headers():
    return {
        'Authorization': f'Bearer {API_KEY}'
    }

# Home page with the form to list devices
@app.route('/')
def home():
    return render_template('devices.html')

# Fetch all devices from info-beamer and log device structure
@app.route('/devices', methods=['GET'])
def list_devices():
    try:
        response = requests.get(f'{BASE_URL}device/list', headers=get_headers())
        
        if response.status_code == 200:
            devices = response.json().get('devices', [])
            print(f"Device structure: {devices}")  # Log device structure for debugging
            return jsonify(devices)
        else:
            return jsonify({'status': 'failed', 'message': 'Failed to fetch devices'}), response.status_code
    except Exception as e:
        print(f"Error fetching devices: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Restart a single device
@app.route('/restart_device/<device_id>', methods=['POST'])
def restart_device(device_id):
    try:
        response = requests.post(f'{BASE_URL}device/{device_id}/reboot', headers=get_headers())
        
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': f'Device {device_id} rebooted successfully'})
        else:
            return jsonify({'status': 'failed', 'message': 'Failed to restart device'}), response.status_code
    except Exception as e:
        print(f"Error restarting device: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Restart multiple devices
@app.route('/restart_devices', methods=['POST'])
def restart_devices():
    device_ids = request.json.get('device_ids', [])
    
    if not device_ids:
        return jsonify({'status': 'failed', 'message': 'No devices selected'}), 400
    
    results = []
    for device_id in device_ids:
        try:
            response = requests.post(f'{BASE_URL}device/{device_id}/reboot', headers=get_headers())
            if response.status_code == 200:
                results.append({'device_id': device_id, 'status': 'success'})
            else:
                results.append({'device_id': device_id, 'status': 'failed'})
        except Exception as e:
            results.append({'device_id': device_id, 'status': f'error: {str(e)}'})
    
    return jsonify({'results': results})

# Upload asset and return asset ID
@app.route('/upload_asset', methods=['POST'])
def upload_asset():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # Save file securely and generate asset ID
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Simulate generating an asset ID
        asset_id = len(os.listdir(app.config['UPLOAD_FOLDER']))  # Incremental asset ID
        print(f"Uploaded asset: {filename}, asset_id: {asset_id}")

        return jsonify({'asset_id': asset_id})

if __name__ == '__main__':
    app.run(debug=True)
