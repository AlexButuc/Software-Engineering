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
import numpy as np

from weather_service import WeatherService
from config import JCDECAUX_API_KEY, JCDECAUX_CONTRACT_NAME, GOOGLE_MAPS_API_KEY
from occupancy_forecast import load_model, forecast_occupancy

app = Flask(__name__)
weather_service = WeatherService()

# Global variable to store bike locations (from JCDecaux)
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
        print(f"[DEBUG] Loaded bike data from {newest_file}")

def fetch_and_save_bike_data():
    url = f"https://api.jcdecaux.com/vls/v1/stations?contract={JCDECAUX_CONTRACT_NAME}&apiKey={JCDECAUX_API_KEY}"
    
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
                print(f"[DEBUG] Updated bike data at {timestamp}")
                
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
    return render_template("map.html", api_key=GOOGLE_MAPS_API_KEY)

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
            # to work with the ML model I added the numeric station ID from the API
            "id": loc.get("number"),
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

# changed the loading file to be a bit more robust
# Determine the current directory of the app.py file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# This constructs the full path to our model file
MODEL_PATH = os.path.join(BASE_DIR, "ml_model", "bike_station_rf_model.pkl")

# This will load the pickle model using the constructed file path
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)
print("[DEBUG] Loaded ML model")

# 2) Load historical average dictionaries for occupancy
# These files were saved during training.

with open(os.path.join(BASE_DIR, "ml_model", "avg_docks.pkl"), "rb") as f:
    avg_docks = pickle.load(f)
with open(os.path.join(BASE_DIR, "ml_model","avg_capacity.pkl"), "rb") as f:
    avg_capacity = pickle.load(f)
print("[DEBUG] Loaded historical average occupancy data")

# 3) Weather forecast function (returns only temperature and humidity)
def get_weather_forecast(city, date_str):
    """
    Fetch current weather data for the given city.
    Returns a dictionary with keys 'temperature' and 'humidity'.
    
    """
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,                      # e.g., "Dublin"
            'appid': "0c6e82fcf592941a58ea878933d06911",
            'units': 'metric'
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        # Debug the raw weather data
        print(f"[DEBUG] Raw weather data for {city}: {data}")
        temperature = data['main']['temp']
        humidity    = data['main']['humidity']
        
        return {
            'temperature': temperature,
            'humidity': humidity
        }
    except Exception as e:
        print(f"Error calling OpenWeather for city={city}: {e}")
        return None

# 4) Helper function to retrieve live station info (capacity and available docks)
def get_station_info(station_id):
    """
    Given a station_id, searches the latest JCDecaux data (in locations) for the actual capacity
    and calculates available docks as (capacity - available_bikes).
    """
    for loc in locations:
        # Adjust based on your data keys (e.g., "number" or "station_id")
        if loc.get("number") == station_id or loc.get("station_id") == station_id:
            capacity = loc.get("bike_stands")
            available_bikes = loc.get("available_bikes")
            if capacity is not None and available_bikes is not None:
                num_docks_available = capacity - available_bikes
                print(f"[DEBUG] Station {station_id}: capacity={capacity}, available_docks={num_docks_available}")
                return capacity, num_docks_available
    print(f"[DEBUG] Station info not found for station_id {station_id}")
    return None, None

# 5) Prediction function: use live station data and weather to create input for the model
def predict_bike_availability(station_id, city, year, month, day, hour, minute):
    date_str_ymd = f"{year:04d}-{month:02d}-{day:02d}"
    time_str_hm = f"{hour:02d}:{minute:02d}"
    dt = datetime.strptime(f"{date_str_ymd} {time_str_hm}", "%Y-%m-%d %H:%M")

    # Get current weather data
    weather_features = get_weather_forecast(city, date_str_ymd)
    if weather_features is None:
        raise Exception("Weather data unavailable.")
    
    current_date = datetime.now().date()
    if dt.date() == current_date:
        capacity, num_docks_available = get_station_info(station_id)
        if capacity is None or num_docks_available is None:
            raise Exception(f"Station info not available for station_id {station_id}.")
        print(f"[DEBUG] Using live occupancy data for station {station_id}")
    else:
         # For future dates, use dynamic occupancy forecast.
        try:
            occupancy_model = load_model(station_id)
            forecasted_occupancy = forecast_occupancy(occupancy_model, dt)
            capacity = avg_capacity.get(station_id)  # Assume capacity remains constant over time.
            num_docks_available = forecasted_occupancy
            print(f"[DEBUG] Using dynamic occupancy forecast for station {station_id}")
        except Exception as e:
            # Fallback to historical averages
            capacity = avg_capacity.get(station_id)
            num_docks_available = avg_docks.get(station_id)
            print(f"[DEBUG] Using historical occupancy averages for station {station_id} due to error: {e}")
    
    day_of_week = dt.weekday()
    
    # Build input DataFrame for the model
    input_data = pd.DataFrame([{
        'station_id': station_id,
        'year': dt.year,
        #'month': dt.month,

        #'hour': dt.hour,
        'day_of_week': day_of_week,
        'num_docks_available': num_docks_available,
        'capacity': capacity,
        'temperature': weather_features['temperature'],
        'humidity': weather_features['humidity']
    }])

    print(f"[DEBUG] Input data for prediction:\n{input_data}")
    prediction = model.predict(input_data)
    return float(prediction[0])

@app.route("/predict_bike_availability", methods=["GET"])
def predict_bike_availability_route():
    """
    Example:
      GET /predict_bike_availability?station_id=32&city=Dublin&year=2024&month=12&day=17&hour=5&minute=40
    """
    try:
        station_id = request.args.get("station_id", type=int)
        city = request.args.get("city", default="Dublin")
        year = request.args.get("year", type=int)
        month = request.args.get("month", type=int)
        day = request.args.get("day", type=int)
        hour = request.args.get("hour", type=int)
        minute = request.args.get("minute", type=int)

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

        #changed it a little so the user could see the prediction to the nearest whole number
        rounded_value = round(predicted_value)
        return jsonify({"predicted_bikes": rounded_value})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    load_bike_data()

    cap, docks = get_station_info(110)
    print(f"Station 110: capacity = {cap}, available docks = {docks}")

    os.makedirs('static/images', exist_ok=True)
    app.run(host="0.0.0.0", port=80, debug=False)