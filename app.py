from flask import Flask, render_template, jsonify
import json
from weather_service import WeatherService

app = Flask(__name__)
weather_service = WeatherService()

# Load locations from JSON file
with open("bike_data_2025-02-24_20-06-54.json", "r") as file:
    locations = json.load(file)

@app.route("/")
def index():
    return render_template("index.html", api_key="AIzaSyArbqOt0_HIapSIWPwmKJqjwfg8TDi6_6M")

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

if __name__ == '__main__':
    app.run(debug=True)
