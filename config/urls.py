from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from products.sitemaps import ProductSitemap,StaticViewSitemap
from django.http import HttpResponse


sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
}


def robots_txt(request):
    return HttpResponse(
        "User-agent: *\n"
        "Allow: /\n\n"
        "Sitemap: https://golabherachik.ir/sitemap.xml",
        content_type="text/plain",
    )


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("products.urls")),
    path("orders/", include("orders.urls")),

    path("robots.txt", robots_txt),

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)