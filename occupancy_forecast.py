import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import pickle
from datetime import datetime

data = pd.read_csv("D:/UCD/Github/Software-Engineering/ml_model/bike_weather_data.xls")

data["timestamp"] = pd.to_datetime(data["last_reported"])
data = data.sort_values("timestamp")

def train_occupancy_model(data, station_id, order=(1,1,1)):
    """
        Trains an ARIMA time series model for number_docks_available 
        for each station
    
    """ 
    station_data = data[data["station_id"] == station_id].copy()
    if station_data.empty:
        raise Exception(f"No data for station {station_id}.")

    station_data.set_index("timestamp", inplace = True)
    station_data = station_data.sort_index()
    
    # Resample occupancy data to hourly frequency (adjust frequency as needed)
    occupancy_ts = station_data["num_docks_available"].resample("H").mean()
    occupancy_ts = occupancy_ts.fillna(method = "ffill")  

    model = ARIMA(occupancy_ts, order=order).fit()
    return model

def load_model(station_id):
    filename = f"occupancy_model_station_{station_id}.pkl"
    with open(filename, "rb") as file:
        model = pickle.load(file)
    return model

def forecast_occupancy(model, target_datetime):
    """
    Forecasts the num_dock_available at target_datetime using ARIMA model
    Assumess the model has been trained on hourly data
    """
    last_time = model.data.endog.index[-1]

    steps = int((target_datetime - last_time).total_seconds() // 3600)
    if steps < 1:
        steps = 1

    forecast_Series = model.forecast(steps=steps)
    return forecast_series.iloc[-1]

stations = data["station_id"].unique()
trained_stations = {}

for station in stations:
    try:
        model = train_occupancy_model(data, station)
        filename = f"occupancy_model_station_{station}.pkl"
        with open(filename, "wb")as file:
            pickle.dump(model, file)
        trained_stations[station] = filename
        print(f"Trained and saved occupancy model for station {station} as {filename}.")
    except Exception as e:
        print(f"Error training model for station {station}: {e}")

with open("trained_stations.pkl", "wb") as file:
    pickle.dump(trained_stations, file)
print("Saved trained stations dictionary to 'trained_stations.pkl'.")    