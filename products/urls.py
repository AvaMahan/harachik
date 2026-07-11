from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.home, name="home"),  # همون صفحه اصلی/لیست
    path("about_detail",views.about_detail,name="about_detail"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
]