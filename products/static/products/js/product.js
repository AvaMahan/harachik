document.addEventListener("DOMContentLoaded", function () {

    const buttons = document.querySelectorAll(".filter-btn");
    const container = document.getElementById("product-items-container");

    buttons.forEach(button => {
        button.addEventListener("click", function () {

            const slug = this.dataset.slug;

            // تغییر حالت active
            buttons.forEach(btn => btn.classList.remove("active"));
            this.classList.add("active");
            document.getElementById("product-items-container").style.opacity = "0.4";
            fetch(`/?remedy=${slug}`, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.text())
            .then(data => {
                container.innerHTML = data;
                   container.style.opacity = "1";
            });
          

        });
    });

});
