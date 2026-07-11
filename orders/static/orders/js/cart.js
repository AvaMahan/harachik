let currentProduct = null;

/* =========================
   STATE
========================= */

let selectedContainers = {};

/* =========================
   CART
========================= */

function getCart() {
    return JSON.parse(localStorage.getItem("cart") || "[]");
}

function saveCart(cart) {
    localStorage.setItem("cart", JSON.stringify(cart));
}

function updateCartCount() {

    const badge = document.getElementById("cartCount");
    if (!badge) return;

    const cart = getCart();

    let totalQty = 0;

    cart.forEach(item => {
        totalQty += item.qty;
    });

    badge.textContent = totalQty;
}

/* =========================
   RENDER OFFCANVAS
========================= */

document.addEventListener("click", function (e) {

    const btn = e.target.closest(".open-product-offcanvas");
    if (!btn) return;

    currentProduct = {
        id: btn.dataset.productId,
        name: btn.dataset.productName
    };

    document.getElementById("offcanvasProductName").textContent =
        btn.dataset.productName;

    const containerCards = document.getElementById("containerCards");
    containerCards.innerHTML = "";

    selectedContainers = {};

    const prices = JSON.parse(btn.dataset.prices || "[]");
    containerCards.scrollLeft = 0;

    prices.forEach(item => {

        const card = document.createElement("div");
        card.className = "container-card";

        card.innerHTML = `
            <div class="container-label">${item.label}</div>
            <div class="container-meta">${item.volume} لیتر</div>
            <div class="container-price">
                ${item.price.toLocaleString("fa-IR")} تومان
            </div>

            <div class="qty-control">
                <button class="qty-minus">-</button>
                <span class="qty-value">0</span>
                <button class="qty-plus">+</button>
            </div>
        `;
         
        card.dataset.id = item.id;
        card.dataset.price = item.price;
        card.dataset.liters = item.volume;

        containerCards.appendChild(card);
    });

    const productCanvas =
    new bootstrap.Offcanvas(
        document.getElementById("productOffcanvas")
    );

productCanvas.show();

// ریست اسکرول بعد از باز شدن
setTimeout(() => {

    document.querySelector(
        "#productOffcanvas .offcanvas-body"
    ).scrollTop = 0;

}, 100);

updateLiveSummary();
});

/* =========================
   MAIN INTERACTION (CLICK + / - + CARD)
========================= */

document.addEventListener("click", function (e) {

    const card = e.target.closest(".container-card");
    if (!card) return;

    const id = card.dataset.id;
    const valueEl = card.querySelector(".qty-value");

    const isPlus = e.target.closest(".qty-plus");
    const isMinus = e.target.closest(".qty-minus");

    /* =========================
       CLICK ON CARD (TOGGLE 1 / 0)
    ========================== */
    if (!isPlus && !isMinus) {

        if (selectedContainers[id]) {

            delete selectedContainers[id];
            card.classList.remove("active");
            valueEl.textContent = 0;

        } else {

            selectedContainers[id] = {
                card: card,
                count: 1
            };

            card.classList.add("active");
            valueEl.textContent = 1;
        }

        updateLiveSummary();
        return;
    }

    /* =========================
       PLUS
    ========================== */
    if (isPlus) {

        if (!selectedContainers[id]) {
            selectedContainers[id] = {
                card: card,
                count: 0
            };
        }

        selectedContainers[id].count++;

        card.classList.add("active");
        valueEl.textContent = selectedContainers[id].count;

        updateLiveSummary();
        return;
    }

    /* =========================
       MINUS
    ========================== */
    if (isMinus) {

        if (!selectedContainers[id]) return;

        selectedContainers[id].count--;

        if (selectedContainers[id].count <= 0) {

            delete selectedContainers[id];
            card.classList.remove("active");
            valueEl.textContent = 0;

        } else {

            valueEl.textContent = selectedContainers[id].count;
        }

        updateLiveSummary();
    }
});

/* =========================
   LIVE SUMMARY
========================= */

function updateLiveSummary() {

    const summaryQty = document.getElementById("summaryQty");
    const totalLiters = document.getElementById("totalLiters");
    const totalPrice = document.getElementById("totalPrice");

    let totalItems = 0;
    let totalL = 0;
    let totalP = 0;

    Object.values(selectedContainers).forEach(item => {

        const count = item.count;
        const card = item.card;

        const liters = parseFloat(card.dataset.liters) || 0;
        const price = parseInt(card.dataset.price) || 0;

        totalItems += count;
        totalL += liters * count;
        totalP += price * count;
    });

    if (summaryQty) summaryQty.textContent = `${totalItems} انتخاب`;
    if (totalLiters) totalLiters.textContent = totalL.toLocaleString("fa-IR");
    if (totalPrice) totalPrice.textContent = totalP.toLocaleString("fa-IR");
}

function showToast(){

    const toast = document.getElementById("toast");

    toast.classList.add("show");

    setTimeout(()=>{
        toast.classList.remove("show");
    },2500);

}

/* =========================
   ADD TO CART
========================= */

document.getElementById("addToCartBtn")
.addEventListener("click", function () {

    if (Object.keys(selectedContainers).length === 0) {
        alert("لطفاً حداقل یک ظرف انتخاب کنید");
        return;
    }

    const cart = getCart();

    Object.values(selectedContainers).forEach(item => {

        const card = item.card;

        cart.push({
            product_id: currentProduct.id,
            product_name: currentProduct.name,

            container_id: card.dataset.id,
            container_label: card.querySelector(".container-label").textContent,

            qty: item.count,
            unit_price: parseInt(card.dataset.price)
        });
    });

    saveCart(cart);
    updateCartCount();

    bootstrap.Offcanvas
        .getInstance(document.getElementById("productOffcanvas"))
        ?.hide();

    // alert("به سبد خرید اضافه شد");
    showToast()
});

/* =========================
   INIT
========================= */

document.addEventListener("DOMContentLoaded", updateCartCount);

/* =========================
   RENDER CART
========================= */

function renderCart() {

    const cart = getCart();

    const itemsBox = document.getElementById("cartItems");
    const totalBox = document.getElementById("cartTotal");

    if (!itemsBox || !totalBox) return;

    itemsBox.innerHTML = "";

    let totalPrice = 0;
    let totalQty = 0;

    if (cart.length === 0) {

        itemsBox.innerHTML = `
            <div class="text-center text-muted py-5">

                <i class="bi bi-cart-x fs-1"></i>

                <p class="mt-3">

                    سبد خرید شما خالی است

                </p>

            </div>
        `;

        totalBox.textContent = "0 تومان";
        return;
    }

    cart.forEach((item, index) => {

        const rowTotal = item.qty * item.unit_price;

        totalPrice += rowTotal;
        totalQty += item.qty;
itemsBox.innerHTML += `
<div class="card cart-item">

    <div class="card-body">

        <div class="d-flex justify-content-between">

            <div>
                <div class="fw-bold">${item.product_name}</div>
                <small class="text-muted">${item.container_label}</small>
            </div>

            <button class="btn btn-link text-danger p-0"
                    onclick="removeFromCart(${index})">
                ✕
            </button>

        </div>

        <div class="d-flex justify-content-between align-items-center mt-2">

            <span>
                ${item.qty} × ${item.unit_price.toLocaleString("fa-IR")}
            </span>

            <strong class="text-success">
                ${rowTotal.toLocaleString("fa-IR")} تومان
            </strong>

        </div>

    </div>

</div>
`;
    });

    totalBox.textContent =
        totalPrice.toLocaleString("fa-IR") + " تومان";
}

/* =========================
   REMOVE FROM CART
========================= */

function removeFromCart(index) {

    const cart = getCart();

    cart.splice(index, 1);

    saveCart(cart);

    updateCartCount();

    renderCart();
}

/* =========================
   OPEN CART
========================= */

document
.getElementById("cartBtn")
.addEventListener("click", function (e) {

    e.preventDefault();

    renderCart();

    new bootstrap.Offcanvas(
        document.getElementById("cartOffcanvas")
    ).show();

});

function fillOrderSummary() {

    const cart = getCart();

    const box =
        document.getElementById("orderCartSummary");

    const totalBox =
        document.getElementById("orderCartTotal");

    if (!box || !totalBox) return;

    box.innerHTML = "";

    let total = 0;

    cart.forEach(item => {

        const rowTotal =
            item.qty * item.unit_price;

        total += rowTotal;

        box.innerHTML += `

        <div class="border rounded p-2 mb-2">

            <div class="fw-bold">

                ${item.product_name}

            </div>

            <div class="small text-muted">

                ${item.container_label}

            </div>

            <div class="d-flex justify-content-between mt-2">

                <span>

                    ${item.qty} عدد

                </span>

                <strong>

                    ${rowTotal.toLocaleString("fa-IR")}
                    تومان

                </strong>

            </div>

        </div>

        `;
    });

    totalBox.textContent =
        total.toLocaleString("fa-IR") + " تومان";
}

/* =========================
   CHECKOUT
========================= */

document
.getElementById("checkoutBtn")
.addEventListener("click", function () {

    const cart = getCart();

    if (cart.length === 0) {

        alert("سبد خرید خالی است.");

        return;
    }

    // پر کردن خلاصه سفارش
    fillOrderSummary();

    // بستن سبد خرید
    const cartCanvasEl =
        document.getElementById("cartOffcanvas");

    const cartCanvas =
        bootstrap.Offcanvas.getInstance(cartCanvasEl);

    if (cartCanvas) {
        cartCanvas.hide();
    }

    // باز کردن مودال
    const orderModal =
        new bootstrap.Modal(
            document.getElementById("orderModal")
        );

    orderModal.show();

});