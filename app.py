from flask import Flask, render_template, jsonify

app = Flask(__name__)

locations = [
    {"name": "Dublin Castle", "lat": 53.343, "lng": -6.267},
    {"name": "Trinity College", "lat": 53.344, "lng": -6.257},
    {"name": "Guinness Storehouse", "lat": 53.3419, "lng": -6.286},
    {"name": "Temple Bar", "lat": 53.345, "lng": -6.264},
    {"name": "Phoenix Park", "lat": 53.356, "lng": -6.316} 
]

@app.route("/")
def index():
    return render_template("index.html", api_key = "AIzaSyArbqOt0_HIapSIWPwmKJqjwfg8TDi6_6M",locations=locations)

@app.route("/locations")
def get_locations():
    return jsonify(locations)

if __name__ == '__main__':
    app.run(debug=True)