document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.querySelector('.toggle-btn');        // The "X" inside the panel
    const predictionPanel = document.getElementById('prediction-panel');
    const showPredictionsBtn = document.getElementById('show-predictions');
    const predictionForm = document.getElementById('prediction-form');
    const predictedBikesSpan = document.getElementById('predicted-bikes'); // Where you show predictions

    // 1. Hide panel, show "Show Predictions" button when clicking the "X"
    if (toggleBtn && predictionPanel && showPredictionsBtn) {
        toggleBtn.addEventListener('click', function() {
            predictionPanel.style.display = 'none';  
            showPredictionsBtn.style.display = 'block';  // Make the "Show" button visible
        });
    }

    // 2. Show panel, hide "Show Predictions" button when clicking the "Show Predictions"
    if (showPredictionsBtn && predictionPanel) {
        showPredictionsBtn.addEventListener('click', function() {
            predictionPanel.style.display = 'block';  
            showPredictionsBtn.style.display = 'none';  // Hide the "Show" button
        });
    }

    // 3. Handle prediction form submission
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent page refresh
            const formData = new FormData(predictionForm);
            const params = new URLSearchParams(formData).toString();

            // Logging for debug
            console.log("Submitting prediction form with parameters:", params);

            // GET request to Flask endpoint
            fetch(`/predict_bike_availability?${params}`)
                .then(response => response.json())
                .then(data => {
                    if (typeof data.predicted_bikes !== 'undefined') {
                        // Round the prediction to a whole number
                        const roundedPrediction = Math.round(data.predicted_bikes);
                        predictedBikesSpan.textContent = roundedPrediction;
                    } else {
                        predictedBikesSpan.textContent = `Error: ${data.error}`;
                    }
                })
                .catch(error => {
                    console.error('Error fetching prediction:', error);
                    predictedBikesSpan.textContent = 'Error fetching prediction';
                });
        });
    }

});

