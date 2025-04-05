# Dublin Bike Sharing System

A real-time web application that displays Dublin's bike sharing stations with live availability data and weather information. It also predicts availability of bikes at stations.

## Features

- Real-time bike station locations and availability
- Live weather data for Dublin
- Interactive map interface
- Subscription and purchase options
- Automatic data updates every 5 minutes
- Weather data caching to minimize API calls
- Prediction of bike availability 

## Technical Stack

- **Backend**: Python Flask
- **Frontend**: HTML, JavaScript
- **APIs**: 
  - JCDecaux API for bike data
  - OpenWeather API for weather information
  - Google Maps API for mapping

## Project Structure

```
├── app.py              # Main Flask application
├── weather_service.py  # Weather data service
├── static/            # Static assets
├── templates/         # HTML templates
└── *.json            # Bike data files
└── Machine Learning / # Machine Learning files
```

## Setup and Installation

1. Clone the repository
2. Install required dependencies:
   ```
   pip install flask requests
   ```
3. Set up your API keys:
   - JCDecaux API key
   - OpenWeather API key
   - Google Maps API key

4. Run the application:
   ```
   python app.py
   ```

The application should be available at `http://localhost:8080`

## API Endpoints

- `/` - Home page
- `/map` - Interactive map view
- `/locations` - JSON endpoint for bike station data
- `/subscription` - Subscription page
- `/purchase` - Purchase page

## Data Management

- Bike data is automatically fetched every 5 minutes
- Weather data is cached for 10 minutes to minimize API calls
- The system maintains the 5 most recent bike data files
- Old data files are automatically cleaned up


