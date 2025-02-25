from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

# Load locations from JSON file
with open("bike_data_2025-02-24_20-06-54.json", "r") as file:
    locations = json.load(file)

@app.route("/")
def index():
    return render_template("index.html", api_key="AIzaSyArbqOt0_HIapSIWPwmKJqjwfg8TDi6_6M")

@app.route("/locations")
def get_locations():
    # Extract only relevant details for markers
    filtered_locations = [
        {
            "name": loc["name"],
            "lat": loc["position"]["lat"],
            "lng": loc["position"]["lng"]
        }
        for loc in locations
    ]
    return jsonify(filtered_locations)

if __name__ == '__main__':
    app.run(debug=True)
