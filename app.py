from flask import Flask, render_template, jsonify, request
import json
from weather_service import WeatherService
import glob
import os
from datetime import datetime
import requests
import threading
import time

app = Flask(__name__)
weather_service = WeatherService()

# Global variable to store bike locations
locations = []

def get_newest_bike_data_file():
    files = glob.glob("bike_data_*.json")
    if not files:
        return None
    return max(files, key=os.path.getctime)

def cleanup_old_files():
    # Get all bike data files
    files = glob.glob("bike_data_*.json")
    if len(files) <= 5:
        return
    
    # Sort files by creation time (oldest first)
    files.sort(key=os.path.getctime)
    
    # Remove all but the 5 newest files
    files_to_remove = files[:-5]
    for file in files_to_remove:
        try:
            os.remove(file)
            print(f"Removed old file: {file}")
        except Exception as e:
            print(f"Error removing file {file}: {str(e)}")

def load_bike_data():
    global locations
    newest_file = get_newest_bike_data_file()
    if newest_file:
        with open(newest_file, "r") as file:
            locations = json.load(file)

def fetch_and_save_bike_data():
    API_KEY = "64bac24f3e0daee76a46c131c8641d1c4d92ac99"
    CONTRACT_NAME = "Dublin"
    url = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT_NAME}&apiKey={API_KEY}"
    
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"bike_data_{timestamp}.json"
                
                with open(filename, "w") as file:
                    json.dump(data, file, indent=4)
                
                # Update the global locations variable
                global locations
                locations = data
                print(f"Updated bike data at {timestamp}")
                
                # Clean up old files after saving new one
                cleanup_old_files()
            else:
                print(f"Error fetching data: {response.status_code}")
        except Exception as e:
            print(f"Error updating bike data: {str(e)}")
        
        time.sleep(300)  # Wait 5 minutes

# Start the background thread for API updates
update_thread = threading.Thread(target=fetch_and_save_bike_data, daemon=True)
update_thread.start()

# Load initial bike data
load_bike_data()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/map")
def map():
    return render_template("map.html", api_key="AIzaSyArbqOt0_HIapSIWPwmKJqjwfg8TDi6_6M")

@app.route("/subscription")
def subscription():
    return render_template("subscription.html")

@app.route("/locations")
def get_locations():
    # Get Dublin weather once for all locations
    weather_data = weather_service.get_dublin_weather()
    
    # Extract details for markers and add weather data
    filtered_locations = []
    for loc in locations:
        location_data = {
            "name": loc["name"],
            "position": {
                "lat": loc["position"]["lat"],
                "lng": loc["position"]["lng"]
            },
            "bikes": {
                "available": loc["available_bikes"],
                "total": loc["bike_stands"]
            }
        }
        
        if weather_data:
            location_data["weather"] = weather_data
            
        filtered_locations.append(location_data)
    
    return jsonify(filtered_locations)

@app.route("/purchase")
def purchase():
    return render_template("purchase.html")

if __name__ == '__main__':
    # Create static/images directory if it doesn't exist
    os.makedirs('static/images', exist_ok=True)
    app.run(host = "0.0.0.0", port = 80, debug = False)