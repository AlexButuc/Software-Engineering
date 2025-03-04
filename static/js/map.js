// Function to update weather bar
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

function initMap() {
    var dublin = { lat: 53.3498, lng: -6.2603 }; // Dublin center

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 13,
        center: dublin
    });

    // Fetch locations and update weather bar
    fetch('/locations')
        .then(response => response.json())
        .then(data => {
            // Update weather bar with first location's weather (they're all the same)
            if (data.length > 0 && data[0].weather) {
                updateWeatherBar(data[0].weather);
            }

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

                var marker = new google.maps.Marker({
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

                var infoWindow = new google.maps.InfoWindow({
                    content: `
                        <h3>${location.name}</h3>
                        <div style="margin-bottom: 10px;">
                            <strong>Bikes Available:</strong> ${location.bikes.available} / ${location.bikes.total}
                        </div>
                        ${location.weather ? `
                            <p>Temperature: ${location.weather.temperature}°C</p>
                            <p>Weather: ${location.weather.description}</p>
                            <p>Wind Speed: ${location.weather.wind_speed} m/s</p>
                            <p>Humidity: ${location.weather.humidity}%</p>
                            <p>Last Updated: ${location.weather.timestamp}</p>
                        ` : '<p>Weather data unavailable</p>'}
                    `
                });

                marker.addListener('click', function() {
                    infoWindow.open(map, marker);
                });
            });
        })
        .catch(error => console.error("Error fetching locations:", error));

    // Add Search Box
    var input = document.getElementById('search-box');
    var searchBox = new google.maps.places.SearchBox(input);
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

    searchBox.addListener('places_changed', function() {
        var places = searchBox.getPlaces();
        if (places.length == 0) return;

        var bounds = new google.maps.LatLngBounds();
        places.forEach(place => {
            if (!place.geometry) return;
            if (place.geometry.viewport) bounds.union(place.geometry.viewport);
            else bounds.extend(place.geometry.location);
        });

        map.fitBounds(bounds);
    });
} 