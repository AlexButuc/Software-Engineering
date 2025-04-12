import requests
import time
import json
from datetime import datetime

# API
API_KEY = "64bac24f3e0daee76a46c131c8641d1c4d92ac99"
CONTRACT_NAME = "Dublin"
url = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT_NAME}&apiKey={API_KEY}"

# function to extract satation info (Capacity and available docks)
def extract_station_info(station):
    # Assume 'bike_stands' is the total capacity 
    # and 'available_bike_stands' indicates the number of docks available.
    capacity = station.get("bike_stands")  # <-- CHANGED: extract capacity from "bike_stands"
    available_docks = station.get("available_bike_stands")  # <-- CHANGED: extract available docks
    return capacity, available_docks

# Function to save API data to a JSON file
def save_to_json(data):
    for station in data:
        capacity, available_docks = extract_station_info(station)
        print(f"Station {station.get('number')}: Capacity = {capacity}, Available Docks = {available_docks}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"bike_data_{timestamp}.json"

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

    print(f"Data saved to {filename}")

# Main loop to fetch and save data
while True:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"Fetched data at {time.strftime('%H:%M:%S')}")
        save_to_json(data)
    else:
        print("Error fetching data:", response.status_code)

    time.sleep(300)
