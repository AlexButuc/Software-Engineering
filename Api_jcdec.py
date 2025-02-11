import mysql.connector
import requests
import time
from datetime import datetime

# API
API_KEY = "64bac24f3e0daee76a46c131c8641d1c4d92ac99"
CONTRACT_NAME = "Dublin"
url = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT_NAME}&apiKey={API_KEY}"

#RDS Database Connection Details
db_host = "database-1.cv4842ms2b5l.eu-north-1.rds.amazonaws.com"
db_name = "my_bike_data"
db_user = "admin"
db_password = "P*B&a33v+!7xj+*"
db_port = "3306" 
ssl_ca = "eu-north-1-bundle.pem" 

# Connect to RDS MySQL 
def connect_to_db():
    return mysql.connector.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port,
        ssl_ca=ssl_ca,  
        ssl_disabled=False  
    )

# Function to update RDS with new station data
def update_rds(stations_data):
    conn = connect_to_db()
    cursor = conn.cursor()

    for station in stations_data:
        timestamp = datetime.now()

        # Insert new data into station_history table to keep track of data over time
        query_insert = """
        INSERT INTO station_history (station_id, name, banking, status, available_bikes, available_stands, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            query_insert,
            (
                station['number'],
                station['name'],
                station['banking'],
                station['status'],
                station['available_bikes'],
                station['available_bike_stands'],
                timestamp
            )
        )

    conn.commit()
    cursor.close()
    conn.close()

# Main loop to fetch data 
while True:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"Fetched data at {time.strftime('%H:%M:%S')}")
        update_rds(data)
    else:
        print("Error fetching data:", response.status_code)

    time.sleep(300) 
