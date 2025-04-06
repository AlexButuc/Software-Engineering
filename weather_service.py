import requests
from datetime import datetime
import os

# The ``API key
OPENWEATHER_API_KEY = "0c6e82fcf592941a58ea878933d06911"

class WeatherService:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        # Dublin coordinates
        self.dublin_lat = 53.3498
        self.dublin_lon = -6.2603
        self.last_weather = None
        self.last_update = None
        
    def get_dublin_weather(self):
        """
        Fetch weather data for Dublin
        Updates cache if data is older than 10 minutes
        """
        current_time = datetime.now()
        
        # If we have cached data less than 10 minutes old, return it
        if (self.last_weather and self.last_update and 
            (current_time - self.last_update).total_seconds() < 600):
            return self.last_weather
            
        try:
            params = {
                'lat': self.dublin_lat,
                'lon': self.dublin_lon,
                'appid': self.api_key,
                'units': 'metric'  # For Celsius
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            weather_data = response.json()
            
            # Extract relevant weather information
            processed_data = {
                'temperature': round(weather_data['main']['temp']),
                'description': weather_data['weather'][0]['description'],
                'icon': weather_data['weather'][0]['icon'],
                'wind_speed': weather_data['wind']['speed'],
                'humidity': weather_data['main']['humidity'],
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Update cache
            self.last_weather = processed_data
            self.last_update = current_time
            
            return processed_data
            
        except Exception as e:
            print(f"Error fetching Dublin weather data: {e}")
            return None
            
    def get_weather(self, lat, lon):
        """
        Returns Dublin weather data for all locations
        """
        return self.get_dublin_weather() 