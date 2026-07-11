from django.contrib import admin
from .models import Category, Product, Benefit, ProductContainerPrice,Remedy

class ProductContainerPriceInline(admin.TabularInline):
    model = ProductContainerPrice
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Remedy)
class RemedyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
  
@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ("title",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductContainerPriceInline]
    list_display = (
        "name","volume_liter",
        "category",
        "starting_from_display", # نمایش قیمت شروع از
        "available",
        "is_active",
    )
    list_filter = ("category", "available", "is_active")
    search_fields = ("name", "category__name")
    filter_horizontal = ('remedies',) #

    def starting_from_display(self, obj):
        from django.contrib.humanize.templatetags.humanize import intcomma
        return f"{intcomma(obj.starting_from_price)} تومان"
    starting_from_display.short_description = "شروع قیمت از"
