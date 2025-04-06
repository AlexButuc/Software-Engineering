from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

# Google Maps API key
GOOGLE_MAPS_API_KEY = 'AIzaSyCI_Cqvg1e7UTI33kicmL-qtaQAtlXtW10'

# Function to load the latest JSON file
def load_latest_json():
    json_files = [f for f in os.listdir() if f.startswith("bike_data_") and f.endswith(".json")]
    
    if not json_files:
        return []

    latest_file = max(json_files, key=os.path.getctime)  # Get the most recently modified JSON file
    
    with open(latest_file, "r") as file:
        data = json.load(file)

    return data

@app.route('/')
def index():
    stations = load_latest_json()  # Load JSON data instead of querying the database
    return render_template("index.html", stations=stations, google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/api/stations')
def api_stations():
    return jsonify(load_latest_json())  # API endpoint to return JSON data

if __name__ == '__main__':
    app.run(debug=True)
