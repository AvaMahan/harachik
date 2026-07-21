from django.db import models
from slugify import slugify
from django.urls import reverse
class Benefit(models.Model):
    title = models.CharField("عنوان عرق",max_length=200)
    icon = models.CharField("ایکون کنار فواید",max_length=100, blank=True, null=True)
      
    class Meta:
        verbose_name = " فواید"
        verbose_name_plural = "فواید  عرقیجات "
    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی عرقیجات "

    def __str__(self):
        return self.name
    
# ۱. اضافه کردن مدل جدید برای خواص درمانی
class Remedy(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام بیماری یا هدف درمانی")
    slug = models.SlugField(unique=True, allow_unicode=True, verbose_name="اسلاگ (برای آدرس سایت)")

    icon_class = models.CharField(
        max_length=50, 
        default="fa-leaf", 
        verbose_name="کد آیکون (FontAwesome)",
        help_text="مثلاً: fa-leaf یا fa-heart")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "هدف درمانی"
        verbose_name_plural = "اهداف درمانی"

    def __str__(self):
        return self.name
class Product(models.Model):
    # دسته‌بندی
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1, verbose_name="دسته‌بندی")

     # ۲. اضافه کردن رابطه چند‌به‌چند به بیماری‌ها
    remedies = models.ManyToManyField(Remedy, related_name="remedy_products", verbose_name="خواص درمانی (برای جستجو و فیلتر)")

    # اطلاعات اصلی
    name = models.CharField("نام محصول",max_length=200,)
    slug = models.SlugField("اسلاگ",unique=True, blank=True)
    description = models.TextField("توضیحات",blank=True)
    brand = models.CharField("برند",max_length=100, default="هراچیک")

    # قیمت‌های قدیمی (حفظ شده برای جلوگیری از خطای دیتابیس)
    price = models.PositiveIntegerField("قیمت",default=0)
    discount_price = models.PositiveIntegerField("قیمت تخفیف",blank=True, null=True)

    # مشخصات محصول
    volume_liter = models.DecimalField("حجم ظرف",max_digits=3, decimal_places=1, help_text="حجم پایه (مثلاً 1.0)", default=1.0)

    # موجودی و وضعیت
    stock = models.PositiveIntegerField( "چند لیترعرق در کارگاست",default=0)
    image = models.ImageField("آپلود عکس",upload_to='product/', blank=True)
    available = models.BooleanField("موجوده یا نه",default=True)
    is_active = models.BooleanField("نشون بده در سایت",default=True)

    # اطلاعات تکمیلی
    usage_instruction = models.TextField("نحوه مصرف",blank=True, help_text="نحوه مصرف محصول")
    usage_time = models.TextField("زمان مصرف",blank=True, help_text="بهترین زمان مصرف")
    storage_condition = models.TextField("شرایط نگهداری",blank=True, help_text="شرایط نگهداری")

    benefits = models.ManyToManyField(
        Benefit, blank=True, related_name="products") 
    
    created = models.DateTimeField("زمان ایجاد محصول",auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField("زمان ویرایش محصول",auto_now=True, null=True, blank=True)

    # --- متدهای محاسباتی جدید ---
    @property
    def active_container_prices(self):
        """لیست قیمت‌های فعالی که برای این محصول تعریف شده است"""
        return self.container_prices.filter(is_active=True)


    @property
    def starting_from_price(self):
        """پیدا کردن کمترین قیمت برای نمایش عبارت 'شروع از ...'"""
        prices = self.active_container_prices.values_list('price', flat=True)
        if prices:
            return min(prices)
        return self.price  # اگر قیمت حجمی نداشت، قیمت اصلی را برگرداند
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
        "products:product_detail",
        kwargs={"slug": self.slug}
    )
    
    class Meta:
        verbose_name = " محصولات"
        verbose_name_plural = " محصولات سایت "

    def __str__(self):
        return f"{self.name}"

# --- مدل جدید برای قیمت‌گذاری حجمی ---
class ProductContainerPrice(models.Model):

    CONTAINER_CHOICES = [
        ('1L', 'بطری ۱ لیتری'),
        ('2L', 'بطری ۲ لیتری'),
        ('4L', 'بطری ۴ لیتری'),
        ('10L', 'گالن ۱۰ لیتری'),
        ('20L', 'گالن ۲۰ لیتری'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="container_prices",
        verbose_name="محصول"
    )

    container_type = models.CharField(
        max_length=10,
        choices=CONTAINER_CHOICES,
        verbose_name="نوع ظرف"
    )

    price = models.PositiveIntegerField(
        verbose_name="قیمت (تومان)"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_container_type_display()}"
