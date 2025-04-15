import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import pickle
from datetime import datetime

# --- Step 1: Load your historical data ---
data = pd.read_csv("D:/UCD/Github/Software-Engineering/ml_model/bike_weather_data.xls")

# If last_reported is a Unix timestamp, uncomment the following line:
# data['timestamp'] = pd.to_datetime(data['last_reported'], unit='s')
# Otherwise, if last_reported is already in datetime string format, use:
data['timestamp'] = pd.to_datetime(data['last_reported'])

# Sort data by timestamp
data = data.sort_values('timestamp')

# --- Step 2: Define a function to train an ARIMA model for a single station ---
def train_occupancy_model(data, station_id, order=(1, 1, 1)):
    """
    Trains an ARIMA model on the occupancy time series (num_docks_available)
    for the given station.
    """
    station_data = data[data['station_id'] == station_id].copy()
    if station_data.empty:
        raise Exception(f"No data for station {station_id}.")

    # Use the existing 'timestamp' column (from last_reported)
    station_data.set_index('timestamp', inplace=True)
    station_data = station_data.sort_index()

    # Resample occupancy data to hourly frequency (adjust frequency as needed)
    occupancy_ts = station_data['num_docks_available'].resample('H').mean()

    # Fill missing values (forward fill)
    occupancy_ts = occupancy_ts.fillna(method='ffill')

    # Train the ARIMA model; you may later tune the (p,d,q) parameters.
    model = ARIMA(occupancy_ts, order=order).fit()
    return model

# --- NEW: Define a function to load a saved occupancy model for a given station ---
def load_model(station_id):
    """
    Loads the occupancy ARIMA model for the given station from a pickle file.
    """
    filename = f"occupancy_model_station_{station_id}.pkl"
    with open(filename, "rb") as f:
        model = pickle.load(f)
    return model

# --- NEW: Define a function to forecast occupancy for a given target datetime ---
def forecast_occupancy(model, target_datetime):
    """
    Forecasts the occupancy (num_docks_available) at target_datetime using the trained ARIMA model.
    
    Assumes the model was trained on hourly data.
    """
    # Get the last timestamp from the model's data
    last_time = model.data.endog.index[-1]
    # Calculate the number of hours between the last time and target_datetime
    steps = int((target_datetime - last_time).total_seconds() // 3600)
    if steps < 1:
        steps = 1
    # Forecast `steps` ahead and return the forecast for the target time (the last forecasted value)
    forecast_series = model.forecast(steps=steps)
    return forecast_series.iloc[-1]

# --- Step 3: Train an ARIMA model for each station and save them ---
stations = data['station_id'].unique()
trained_stations = {}

for station in stations:
    try:
        model = train_occupancy_model(data, station)
        filename = f"occupancy_model_station_{station}.pkl"
        with open(filename, "wb") as f:
            pickle.dump(model, f)
        trained_stations[station] = filename
        print(f"Trained and saved occupancy model for station {station} as {filename}.")
    except Exception as e:
        print(f"Error training model for station {station}: {e}")

with open("trained_stations.pkl", "wb") as f:
    pickle.dump(trained_stations, f)
print("Saved trained stations dictionary to 'trained_stations.pkl'.")
