let map;
let markers = [];
let bikeLayer;    // We'll store a global reference to the Bicycling Layer
let infoWindow;   // We'll store a single InfoWindow instance here

// Function to update the weather bar at the top
function updateWeatherBar(weatherData) {
    if (!weatherData) {
        document.getElementById('weather-bar').innerHTML = 'Weather data unavailable';
        return;
    }
    
    const weatherBar = document.getElementById('weather-bar');
    weatherBar.innerHTML = `
        <img src="http://openweathermap.org/img/w/${weatherData.icon}.png" alt="${weatherData.description}">
        <div>
            <strong>${weatherData.temperature}°C</strong> | 
            ${weatherData.description} | 
            Wind: ${weatherData.wind_speed} m/s | 
            Humidity: ${weatherData.humidity}%
        </div>
    `;
}

// Function to clear all markers from the map
function clearMarkers() {
    for (let marker of markers) {
        marker.setMap(null);
    }
    markers = [];
}

// Function to update map data (fetch from your Flask endpoint)
function updateMapData() {
    if (!map) {
        console.error('Map not initialized');
        return;
    }

    fetch('/locations')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);
            
            // Update weather bar with the first location's weather (they're all the same)
            if (data.length > 0 && data[0].weather) {
                updateWeatherBar(data[0].weather);
            }

            // Clear existing markers before adding new ones
            clearMarkers();

            data.forEach(location => {
                // Calculate availability percentage
                const availabilityPercent = (location.bikes.available / location.bikes.total) * 100;
                
                // Choose marker color based on availability
                let markerColor;
                if (availabilityPercent >= 66) {
                    markerColor = 'green';
                } else if (availabilityPercent >= 33) {
                    markerColor = 'orange';
                } else {
                    markerColor = 'red';
                }

                // Create the marker
                const marker = new google.maps.Marker({
                    position: { lat: location.position.lat, lng: location.position.lng },
                    map: map,
                    title: `${location.name} (${location.bikes.available}/${location.bikes.total} bikes)`,
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        fillColor: markerColor,
                        fillOpacity: 0.8,
                        strokeWeight: 1,
                        strokeColor: '#ffffff',
                        scale: 10
                    }
                });

                // Optional: Add a Google Street View Static Image for each station
                // (Requires that the same API key has Street View Static API enabled)
                const streetViewImageUrl = `
                https://maps.googleapis.com/maps/api/streetview?size=120x120&location=${location.position.lat},${location.position.lng}&key=AIzaSyArbqOt0_HIapSIWPwmKJqjwfg8TDi6_6M
                `.trim();


                // Build the content for the InfoWindow
                const infoWindowContent = `
                    <div style="text-align:left;">
                        <h3>${location.name}</h3>
                        
                        <!-- Display the optional Street View image -->
                        <img src="${streetViewImageUrl}" 
                             alt="Street View" 
                             style="width:120px;height:auto;margin:5px 0;">

                        <div style="margin-bottom: 10px;">
                            <strong>Bikes Available:</strong> 
                            ${location.bikes.available} / ${location.bikes.total}
                        </div>
                        ${
                            location.weather
                            ? `
                                <p><strong>Temperature:</strong> ${location.weather.temperature}°C</p>
                                <p><strong>Weather:</strong> ${location.weather.description}</p>
                                <p><strong>Wind Speed:</strong> ${location.weather.wind_speed} m/s</p>
                                <p><strong>Humidity:</strong> ${location.weather.humidity}%</p>
                            `
                            : '<p>Weather data unavailable</p>'
                        }
                    </div>
                `;

                // When user clicks the marker, open the single global InfoWindow
                marker.addListener('click', function() {
                    infoWindow.setContent(infoWindowContent);
                    infoWindow.open(map, marker);
                });

                // Keep track of the marker in our markers array
                markers.push(marker);
            });
        })
        .catch(error => {
            console.error('Error fetching locations:', error);
            document.getElementById('weather-bar').innerHTML = 'Error loading data. Please try refreshing the page.';
        });
}

// Initialize the map when Google Maps API is ready
function initMap() {
    console.log('Initializing map...');
    try {
        const dublin = { lat: 53.3498, lng: -6.2603 }; // Dublin center

        // Create the map
        map = new google.maps.Map(document.getElementById('map'), {
            zoom: 13,
            center: dublin,
            mapTypeControl: true,
            streetViewControl: true,
            fullscreenControl: true
        });

        // Create the Bicycling Layer (initially off)
        bikeLayer = new google.maps.BicyclingLayer();

        // Create a single InfoWindow instance that we'll reuse
        infoWindow = new google.maps.InfoWindow();

        // Add the Search Box
        const input = document.getElementById('search-box');
        const searchBox = new google.maps.places.SearchBox(input);
        
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

        // Bias search results within the current map's viewport
        map.addListener('bounds_changed', function() {
            searchBox.setBounds(map.getBounds());
        });

        searchBox.addListener('places_changed', function() {
            const places = searchBox.getPlaces();
            if (places.length === 0) return;

            const bounds = new google.maps.LatLngBounds();
            places.forEach(place => {
                if (!place.geometry) return;
                if (place.geometry.viewport) {
                    bounds.union(place.geometry.viewport);
                } else {
                    bounds.extend(place.geometry.location);
                }
            });
            map.fitBounds(bounds);
        });

        // Load initial data
        updateMapData();

        // Periodically refresh data (every 30 seconds)
        setInterval(updateMapData, 30000);

        console.log('Map initialized successfully');
    } catch (error) {
        console.error('Error initializing map:', error);
        document.getElementById('map').innerHTML = 'Error loading map. Please try refreshing the page.';
    }
}

// Toggle the Bicycling Layer on/off
function toggleBikeLayer() {
    if (!bikeLayer) return;
    if (bikeLayer.getMap()) {
        bikeLayer.setMap(null);
    } else {
        bikeLayer.setMap(map);
    }
}
