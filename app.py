# from flask import Flask, render_template, jsonify, request
# import json
# from weather_service import WeatherService
# import glob
# import os
# from datetime import datetime
# import requests
# import threading
# import time
# import pickle

# app = Flask(__name__)
# weather_service = WeatherService()

# # Global variable to store bike locations
# locations = []

# def get_newest_bike_data_file():
#     files = glob.glob("bike_data_*.json")
#     if not files:
#         return None
#     return max(files, key=os.path.getctime)

# def cleanup_old_files():
#     # Get all bike data files
#     files = glob.glob("bike_data_*.json")
#     if len(files) <= 5:
#         return
    
#     # Sort files by creation time (oldest first)
#     files.sort(key=os.path.getctime)
    
#     # Remove all but the 5 newest files
#     files_to_remove = files[:-5]
#     for file in files_to_remove:
#         try:
#             os.remove(file)
#             print(f"Removed old file: {file}")
#         except Exception as e:
#             print(f"Error removing file {file}: {str(e)}")

# def load_bike_data():
#     global locations
#     newest_file = get_newest_bike_data_file()
#     if newest_file:
#         with open(newest_file, "r") as file:
#             locations = json.load(file)

# def fetch_and_save_bike_data():
#     API_KEY = "64bac24f3e0daee76a46c131c8641d1c4d92ac99"
#     CONTRACT_NAME = "Dublin"
#     url = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT_NAME}&apiKey={API_KEY}"
    
#     while True:
#         try:
#             response = requests.get(url)
#             if response.status_code == 200:
#                 data = response.json()
#                 timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#                 filename = f"bike_data_{timestamp}.json"
                
#                 with open(filename, "w") as file:
#                     json.dump(data, file, indent=4)
                
#                 # Update the global locations variable
#                 global locations
#                 locations = data
#                 print(f"Updated bike data at {timestamp}")
                
#                 # Clean up old files after saving new one
#                 cleanup_old_files()
#             else:
#                 print(f"Error fetching data: {response.status_code}")
#         except Exception as e:
#             print(f"Error updating bike data: {str(e)}")
        
#         time.sleep(300)  # Wait 5 minutes

# # Start the background thread for API updates
# update_thread = threading.Thread(target=fetch_and_save_bike_data, daemon=True)
# update_thread.start()

# # Load initial bike data
# load_bike_data()

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/map")
# def map():
#     return render_template("map.html", api_key="AIzaSyCuA1xC9ReXRyKYZ4eEzXD-Pocky4br5x8")

# @app.route("/subscription")
# def subscription():
#     return render_template("subscription.html")

# @app.route("/locations")
# def get_locations():
#     # Get Dublin weather once for all locations
#     weather_data = weather_service.get_dublin_weather()
    
#     # Extract details for markers and add weather data
#     filtered_locations = []
#     for loc in locations:
#         location_data = {
#             "name": loc["name"],
#             "position": {
#                 "lat": loc["position"]["lat"],
#                 "lng": loc["position"]["lng"]
#             },
#             "bikes": {
#                 "available": loc["available_bikes"],
#                 "total": loc["bike_stands"]
#             }
#         }
        
#         if weather_data:
#             location_data["weather"] = weather_data
            
#         filtered_locations.append(location_data)
    
#     return jsonify(filtered_locations)

# @app.route("/purchase")
# def purchase():
#     return render_template("purchase.html")

# Model_Path = "D:/UCD/Github/Software-Engineering/bike_station_avg_model.pkl"
# with open(Model_Path, 'rb') as file:
#     model = pickle.load(file)
# if __name__ == '__main__':
#     # Create static/images directory if it doesn't exist
#     os.makedirs('static/images', exist_ok=True)
#     app.run(host = "0.0.0.0", port = 8080, debug = False)
from flask import Flask, render_template, jsonify, request
import json
import glob
import os
from datetime import datetime
import requests
import threading
import time

import pickle  # for loading your model
import pandas as pd

from weather_service import WeatherService

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
    files = glob.glob("bike_data_*.json")
    if len(files) <= 5:
        return
    files.sort(key=os.path.getctime)
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
                
                global locations
                locations = data
                print(f"Updated bike data at {timestamp}")
                
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
    return render_template("map.html", api_key="AIzaSyCuA1xC9ReXRyKYZ4eEzXD-Pocky4br5x8")

@app.route("/subscription")
def subscription():
    return render_template("subscription.html")

@app.route("/locations")
def get_locations():
    # Get Dublin weather once for all locations
    weather_data = weather_service.get_dublin_weather()
    
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

# 1) Load your pickle model
MODEL_PATH = "D:/UCD/Software Engineering/Source_Code_ML/bike_station_avg_model.pkl"
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)

# 2) REPLACE STUB WITH A REAL API CALL
def get_weather_forecast(city, date_str):
    """
    Fetch actual *current* weather using city name from OpenWeather's
    current weather endpoint (similar to your WeatherService).
    
    If you need a *future forecast*, use OpenWeather's forecast API instead.
    """
    try:
        # We'll ignore date_str here since it's for current weather only
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,                      # e.g., "Dublin"
            'appid': "0c6e82fcf592941a58ea878933d06911",
            'units': 'metric'
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        # Extract key fields
        temperature = data['main']['temp']          # e.g. 13.95
        humidity    = data['main']['humidity']      # e.g. 83.75
        # There's no "soil_temp_20cm" in the standard response
        # We'll keep a placeholder if your model still expects it:
        soil_temp_20cm = 10.0
        # If your model depends on station 'capacity' or 'num_docks_available',
        # typically you'd fetch that from the station data, not weather. 
        # We'll keep placeholders for demonstration.
        capacity = 16
        num_docks_available = 1
        
        return {
            'avg_air_temperature': temperature,
            'avg_humidity': humidity,
            'avg_soil_temp_20cm': soil_temp_20cm,
            'capacity': capacity,
            'num_docks_available': num_docks_available
        }

    except Exception as e:
        print(f"Error calling OpenWeather for city={city}: {e}")
        # fallback - if error, we can return defaults or None
        return {
            'avg_air_temperature': 13.95,
            'avg_humidity': 83.75,
            'avg_soil_temp_20cm': 8.81,
            'capacity': 16,
            'num_docks_available': 1
        }

# 3) Define a function to make a prediction using the loaded model
def predict_bike_availability(station_id, city, year, month, day, hour, minute):
    date_str_ymd = f"{year:04d}-{month:02d}-{day:02d}"
    time_str_hm = f"{hour:02d}:{minute:02d}"
    dt = datetime.strptime(f"{date_str_ymd} {time_str_hm}", "%Y-%m-%d %H:%M")

    # GET REAL WEATHER using city name from our updated function
    weather_features = get_weather_forecast(city, date_str_ymd)

    input_data = pd.DataFrame([{
        'station_id': station_id,
        'year': dt.year,
        'month': dt.month,
        'day': dt.day,
        'hour': dt.hour,
        'minute': dt.minute,
        'num_docks_available': weather_features['num_docks_available'],
        'capacity': weather_features['capacity'],
        'avg_air_temperature': weather_features['avg_air_temperature'],
        'avg_humidity': weather_features['avg_humidity'],
        'avg_soil_temp_20cm': weather_features['avg_soil_temp_20cm']
    }])

    prediction = model.predict(input_data)
    return float(prediction[0])

# 4) Create a new Flask route for predictions
@app.route("/predict_bike_availability", methods=["GET"])
def predict_bike_availability_route():
    """
    Example:
      GET /predict_bike_availability?station_id=32&city=Dublin&year=2024&month=12&day=17&hour=5&minute=40
    """
    try:
        station_id = request.args.get("station_id", type=int)
        city       = request.args.get("city", default="Dublin")
        year       = request.args.get("year", type=int)
        month      = request.args.get("month", type=int)
        day        = request.args.get("day", type=int)
        hour       = request.args.get("hour", type=int)
        minute     = request.args.get("minute", type=int)

        if None in [station_id, year, month, day, hour, minute]:
            return jsonify({"error": "One or more required parameters are missing"}), 400

        predicted_value = predict_bike_availability(
            station_id=station_id,
            city=city,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute
        )

        return jsonify({"predicted_bikes": predicted_value})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs('static/images', exist_ok=True)
    app.run(host="0.0.0.0", port=8080, debug=False)

