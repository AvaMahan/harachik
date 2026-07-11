/**
 * تابع کمکی برای تبدیل متن به لیست‌های کارتی و شیک
 * @param {string} text - متن ورودی که با ویرگول یا نقطه جدا شده
 * @param {string} icon - ایموجی یا آیکون مورد نظر برای هر آیتم
 */
function createListHTML(text, icon) {
    if (!text || text.trim() === "" || text === "None") {
        return `<div style="text-align:center; padding:30px; color:#bbb;">
                    <p>اطلاعاتی برای این بخش ثبت نشده است.</p>
                </div>`;
    }
    
    // اصلاح اصلی اینجاست: 
    // متن را هم بر اساس ویرگول و هم بر اساس "خط جدید" (Enter) جدا می‌کند
    const items = text.split(/[،,.\n\r]/); 
    
    let html = '<ul class="benefits-list">';
    let itemCount = 0;

    items.forEach((item) => {
        const trimmedItem = item.trim();
        if (trimmedItem !== "") {
            // ایجاد تاخیر زمانی برای انیمیشن ورود هر کارت
            const delay = (itemCount * 0.1).toFixed(1);
            html += `
                <li style="animation-delay: ${delay}s">
                    <span class="check-icon">${icon}</span>
                    <span class="item-text">${trimmedItem}</span>
                </li>`;
            itemCount++;
        }
    });
    
    html += '</ul>';
    return html;
}

/**
 * تابع اصلی باز کردن مودال راهنما
 */
function openGuideModal(name, benefits, usage, time, storage) {
    // ۱. نمایش نام محصول در هدر
    document.getElementById("modal-product-name").innerText = name;

    // ۲. پردازش محتوای هر تب با استفاده از تابع کمکی و آیکون‌های اختصاصی
    document.getElementById("modal-benefits").innerHTML = createListHTML(benefits, "🌿");
    document.getElementById("modal-usage").innerHTML    = createListHTML(usage, "🍵");
    document.getElementById("modal-time").innerHTML     = createListHTML(time, "⏰");
    document.getElementById("modal-storage").innerHTML  = createListHTML(storage, "❄️");

    // ۳. ریست کردن تب‌ها (همیشه وقتی باز می‌شود، تب اول فعال باشد)
    const allContents = document.getElementsByClassName("tab-content");
    const allLinks = document.getElementsByClassName("tab-link");
    
    for (let i = 0; i < allContents.length; i++) {
        allContents[i].classList.remove("active");
        allLinks[i].classList.remove("active");
    }
    
    // فعال کردن محتوا و دکمه تب اول (خواص)
    document.getElementById("tab-benefits").classList.add("active");
    if (allLinks.length > 0) {
        allLinks[0].classList.add("active");
    }

    // ۴. نمایش مودال و قفل کردن اسکرول صفحه
    const modal = document.getElementById("guideModal");
    modal.style.display = "block";
    document.body.style.overflow = "hidden"; 

    // ۵. اسکرول کردن محتوای مودال به بالا (اگر قبلاً باز شده بود)
    const modalBody = modal.querySelector('.hr-modal-body');
    if(modalBody) modalBody.scrollTop = 0;
}

/**
 * تابع جابجایی بین تب‌ها
 */
function openTab(evt, tabId) {
    const tabContents = document.getElementsByClassName("tab-content");
    const tabLinks = document.getElementsByClassName("tab-link");

    // غیرفعال کردن همه محتواها و دکمه‌ها
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].classList.remove("active");
    }
    for (let i = 0; i < tabLinks.length; i++) {
        tabLinks[i].classList.remove("active");
    }

    // فعال کردن تب انتخاب شده
    document.getElementById(tabId).classList.add("active");
    evt.currentTarget.classList.add("active");
}

/**
 * تابع بستن مودال
 */
function closeGuideModal() {
    const modal = document.getElementById("guideModal");
    modal.style.display = "none";
    document.body.style.overflow = "auto"; // آزاد کردن اسکرول صفحه
}
