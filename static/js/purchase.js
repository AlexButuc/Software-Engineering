document.addEventListener('DOMContentLoaded', function () {
    const planSelect = document.getElementById('subscription-plan');
    const priceInput = document.getElementById('price');
    const form = document.getElementById('purchase-form');
    const result = document.getElementById('result');
    const button = form.querySelector('button');

    // Function to update price
    function updatePrice() {
        const selectedOption = planSelect.options[planSelect.selectedIndex];
        const price = selectedOption.getAttribute('data-price');
        priceInput.value = `€${price}`;
    }

    // Update price on change
    planSelect.addEventListener('change', updatePrice);

    // Initial price update
    updatePrice();

    // Handle form submission
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        // Disable the button
        button.disabled = true;

        // Generate a random confirmation code
        const confirmationCode = Math.random().toString(36).substring(2, 10).toUpperCase();

        // Show the confirmation with fade-in effect
        result.innerText = `✅ Your confirmation code: ${confirmationCode}`;
        result.classList.add('visible');

        // Reset the form after a short delay
        setTimeout(() => {
            form.reset();
            updatePrice();
            button.disabled = false;
        }, 2000);
    });
});
