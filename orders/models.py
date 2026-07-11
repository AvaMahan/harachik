
from django.db import models
from django.db import models
from django.utils import timezone


# مدل اعتبار سنجی موبایل
class PhoneVerification(models.Model):

    mobile = models.CharField(max_length=11)

    code = models.CharField(max_length=5)

    created_at = models.DateTimeField(auto_now_add=True)

    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=2)

    def __str__(self):
        return f"{self.mobile} - {self.code}"



# مدل ثبت سفارش
class OrderRequest(models.Model):
    cart_data = models.JSONField(
    verbose_name="اقلام سفارش",
    default=list,
    blank=True
)

    class Status(models.TextChoices):
        NEW = "new", "جدید"
        CONTACTED = "contacted", "تماس گرفته شد"
        DONE = "done", "نهایی شد"
        CANCELED = "canceled", "لغو شد"

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="order_requests",
        verbose_name="محصول",
        null=True,
        blank=True,
    )

    container_price = models.ForeignKey(
        "products.ProductContainerPrice",
        on_delete=models.CASCADE,
        verbose_name="نوع ظرف",
        null=True,
        blank=True,
    )

    full_name = models.CharField("نام و نام خانوادگی", max_length=120)
    mobile = models.CharField("شماره موبایل", max_length=11)
    qty = models.PositiveIntegerField("تعداد", default=0)

    total_liters = models.FloatField(default=0, verbose_name="جمع کل به لیتر")

    city = models.CharField("شهر", max_length=80, blank=True)
    note = models.TextField("توضیحات", blank=True)

    status = models.CharField("وضعیت", max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    ip_address = models.GenericIPAddressField("ip کاربر",null=True, blank=True)
    user_agent = models.CharField("اطلاعات مرورگر کاربر",max_length=255, blank=True)

    sms_sent = models.BooleanField(default=False)
    sms_error = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "لیست سفارش‌ها"

    def __str__(self):
        return f"{self.full_name} - {self.mobile} "


    