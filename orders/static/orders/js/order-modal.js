let pendingFormData = null;

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
}

function normalizeCity(value) {
    return (value || "").trim().replace(/\s+/g, " ").replace(/ي/g, "ی").replace(/ك/g, "ک");
}

function updateShippingRuleUI() {
    const cityInput = document.getElementById("orderCity");
    const yazdRule = document.getElementById("ruleYazd");
    const otherRule = document.getElementById("ruleOther");
    if (!cityInput || !yazdRule || !otherRule) return;
    const city = normalizeCity(cityInput.value);
    const isYazd = city === "یزد";
    yazdRule.classList.remove("fw-bold", "text-success");
    otherRule.classList.remove("fw-bold", "text-warning");
    if (isYazd) {
        yazdRule.classList.add("fw-bold", "text-success");
    } else if (city.length > 0) {
        otherRule.classList.add("fw-bold", "text-warning");
    }
}



function resetOrderModal() {
    pendingFormData = null;
    const productIdInput = document.getElementById("orderProductId");
    const currentProductId = productIdInput ? productIdInput.value : "";
    const form = document.getElementById("orderForm");
    if (form) form.reset();
    if (productIdInput) productIdInput.value = currentProductId;

    document.getElementById("otpBox")?.classList.add("d-none");
    const otpInput = document.getElementById("otpCode");
    if (otpInput) otpInput.value = "";

    const errorBox = document.getElementById("orderError");
    if (errorBox) {
        errorBox.textContent = "";
        errorBox.classList.add("d-none");
    }

    const successBox = document.getElementById("orderSuccess");
    if (successBox) {
        // تغییر مهم: محتوا را اینجا پاک نکنید تا انیمیشن بسته شدن مودال خراب نشود
        successBox.classList.add("d-none");
    }

    const submitBtn = document.getElementById("submitBtn") || document.getElementById("submitOrderBtn");
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = "ثبت سفارش";
        submitBtn.classList.remove("d-none");
    }

    const verifyBtn = document.getElementById("verifyOtpBtn");
    if (verifyBtn) {
        verifyBtn.disabled = false;
        verifyBtn.textContent = "تایید کد و ثبت نهایی";
        verifyBtn.classList.remove("d-none");
    }
}

// ارسال کد تایید (مرحله اول)
document.addEventListener("submit", async function (e) {
    const form = e.target.closest("#orderForm");
    if (!form) return;
    e.preventDefault();

    const submitBtn = document.getElementById("submitBtn") || document.getElementById("submitOrderBtn");
    if (submitBtn.disabled) return; // جلوگیری از کلیک تکراری

    const mobile = form.querySelector('input[name="mobile"]').value;
    const errEl = document.getElementById("orderError");
    if (errEl) { errEl.classList.add("d-none"); errEl.textContent = ""; }

    // غیرفعال کردن دکمه
    submitBtn.disabled = true;
    const originalBtnText = submitBtn.textContent;
    submitBtn.textContent = "در حال ارسال کد...";

pendingFormData = new FormData(form);

pendingFormData.append(
    "cart",
    localStorage.getItem("cart") || "[]"
);

    try {
        const res = await fetch("/orders/send-code/", {
            method: "POST",
            body: new URLSearchParams({ mobile: mobile }),
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest",
            }
        });
        const data = await res.json();

        if (!data.ok) {
            errEl.textContent = data.error || "خطا در ارسال کد";
            errEl.classList.remove("d-none");
            submitBtn.disabled = false;
            submitBtn.textContent = originalBtnText;
            return;
        }

        document.getElementById("otpBox").classList.remove("d-none");
        submitBtn.classList.add("d-none"); 
        document.getElementById("otpCode").focus();

    } catch (error) {
        errEl.textContent = "خطا در ارتباط با سرور";
        errEl.classList.remove("d-none");
        submitBtn.disabled = false;
        submitBtn.textContent = originalBtnText;
    }
});

// تایید کد و ثبت نهایی (مرحله دوم)
document.addEventListener("click", async function (event) {
    if (!event.target.matches("#verifyOtpBtn")) return;

    const verifyBtn = event.target;
    if (verifyBtn.disabled) return; // جلوگیری از کلیک تکراری

    const otpValue = document.getElementById("otpCode").value.trim();
    const mobileValue = document.querySelector('input[name="mobile"]').value.trim();
    const errorBox = document.getElementById("orderError");
    const successBox = document.getElementById("orderSuccess");

    if (!otpValue) {
        errorBox.textContent = "کد تایید را وارد کنید";
        errorBox.classList.remove("d-none");
        return;
    }

    // غیرفعال کردن دکمه تایید
    verifyBtn.disabled = true;
    const originalText = verifyBtn.textContent;
    verifyBtn.textContent = "در حال ثبت سفارش...";

    try {
        const res = await fetch("/orders/verify-code/", {
            method: "POST",
            body: new URLSearchParams({ mobile: mobileValue, code: otpValue }),
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest",
            }
        });
        const data = await res.json();

        if (!data.ok) {
            errorBox.textContent = data.error || "کد تایید نامعتبر است";
            errorBox.classList.remove("d-none");
            verifyBtn.disabled = false;
            verifyBtn.textContent = originalText;
            return;
        }

        const orderRes = await fetch("/orders/create/", {
            method: "POST",
            body: pendingFormData,
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest",
            }
        });
        const orderData = await orderRes.json();
       

        if (!orderData.ok) {
            errorBox.textContent = orderData.error || "ثبت سفارش ناموفق بود";
            errorBox.classList.remove("d-none");
            verifyBtn.disabled = false;
            verifyBtn.textContent = originalText;
            return;
        }

        // موفقیت کامل
        errorBox.classList.add("d-none");
        successBox.classList.remove("d-none");
        verifyBtn.classList.add("d-none");
         if(orderData.ok){
            localStorage.removeItem("cart");

        updateCartCount();
        } // مخفی کردن دکمه تایید

        setTimeout(() => {
            const modalEl = document.getElementById("orderModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            
            // وقفه کوتاه برای اتمام انیمیشن بستن مودال قبل از ریست کامل
            setTimeout(resetOrderModal, 500);
        }, 2500);

    } catch (err) {
        errorBox.textContent = "خطا در ارتباط با سرور";
        errorBox.classList.remove("d-none");
        verifyBtn.disabled = false;
        verifyBtn.textContent = originalText;
    }
});

// سایر Listenerها
document.addEventListener("input", function (e) {
    if (e.target.id === "orderCity") updateShippingRuleUI();
    // if (e.target.id === "orderQty") updateOrderSummary();
});
// document.addEventListener("change", function (e) {
//     if (e.target.id === "containerType") updateOrderSummary();
// });
