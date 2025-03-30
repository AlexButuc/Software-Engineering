document.addEventListener("DOMContentLoaded", function() {
    const flipCards = document.querySelectorAll(".flip-card");

    flipCards.forEach(card => {
        card.addEventListener("click", function() {
            this.querySelector(".flip-card-inner").classList.toggle("flipped");
        });
    });
});
