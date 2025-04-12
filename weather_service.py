import requests
from datetime import datetime
import os

# The ``API key
OPENWEATHER_API_KEY = "0c6e82fcf592941a58ea878933d06911"

class WeatherService:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        # For current weather:
        self.base_url_current = "http://api.openweathermap.org/data/2.5/weather"
        # For forecast data:
        self.base_url_forecast = "http://api.openweathermap.org/data/2.5/forecast"
        # Dublin coordinates
        self.dublin_lat = 53.3498
        self.dublin_lon = -6.2603
        # Cache for current weather (10-minute cache)
        self.last_weather = None
        self.last_update = None

    def get_dublin_weather(self):
        """
        Fetch current weather data for Dublin.
        Cached for 10 minutes to reduce API calls for the map page.
        Returns a dictionary with keys: temperature, humidity, description, icon, wind_speed, and timestamp.
        """
        current_time = datetime.now()
        # Return cached weather if it's less than 10 minutes old.
        if (self.last_weather and self.last_update and 
            (current_time - self.last_update).total_seconds() < 600):
            return self.last_weather
        
        try:
            params = {
                'lat': self.dublin_lat,
                'lon': self.dublin_lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(self.base_url_current, params=params)
            response.raise_for_status()
            weather_data = response.json()
            processed_data = {
                'temperature': round(weather_data['main']['temp']),
                'description': weather_data['weather'][0]['description'],
                'icon': weather_data['weather'][0]['icon'],
                'wind_speed': weather_data['wind']['speed'],
                'humidity': weather_data['main']['humidity'],
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.last_weather = processed_data
            self.last_update = current_time
            return processed_data
        except Exception as e:
            print(f"Error fetching Dublin weather data: {e}")
            return None

    def get_dublin_forecast(self, target_datetime):
        """
        Fetch forecast weather data for Dublin using the 5-day/3-hour forecast endpoint.
        This method returns the forecast information closest to the target_datetime.
        Useful for predicting future conditions.
        Returns a dictionary with keys: temperature, humidity, and forecast_time.
        """
        current_date = datetime.now().date()
        if target_datetime.date() == current_date:
            return self.get_dublin_weather()
        try:
            params = {
                'lat': self.dublin_lat,
                'lon': self.dublin_lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(self.base_url_forecast, params=params)
            response.raise_for_status()
            forecast_data = response.json()
            # 'list' contains forecasts at 3-hour intervals
            closest_forecast = None
            min_diff = None
            for entry in forecast_data.get('list', []):
                forecast_time = datetime.fromtimestamp(entry['dt'])
                diff = abs((forecast_time - target_datetime).total_seconds())
                if min_diff is None or diff < min_diff:
                    min_diff = diff
                    closest_forecast = entry
            if closest_forecast:
                processed_forecast = {
                    'temperature': round(closest_forecast['main']['temp']),
                    'humidity': closest_forecast['main']['humidity'],
                    'forecast_time': closest_forecast['dt_txt']
                }
                return processed_forecast
            else:
                return None
        except Exception as e:
            print(f"Error fetching forecast data: {e}")
            return None

    def get_weather(self, lat, lon):
        """
        Returns Dublin weather data for all locations (current weather).
        """
        return self.get_dublin_weather()