import requests
import time
import json
from datetime import datetime

# API
API_KEY = "64bac24f3e0daee76a46c131c8641d1c4d92ac99"
CONTRACT_NAME = "Dublin"
url = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT_NAME}&apiKey={API_KEY}"

# Function to save API data to a JSON file
def save_to_json(data):
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
