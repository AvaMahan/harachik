from django.shortcuts import render,get_object_or_404
from .models import Product,Category,Remedy

def home(request):
    remedy_slug = request.GET.get("remedy")

    products = Product.objects.all()

    if remedy_slug and remedy_slug != "all":
        products = products.filter(remedies__slug=remedy_slug)

    remedies = Remedy.objects.all()

    # اگر درخواست AJAX بود فقط لیست محصولات را برگردان
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "products/_product_list_items.html", {
            "products": products
        })

    return render(request, "home.html", {
        "products": products,
        "remedies": remedies
    })

def product_list(request):
  
    category_slug=request.GET.get("category")#رفتن slug دسته‌بندی از URL

    products=Product.objects.filter(is_active=True,available=True).order_by('-created')

    categories=Category.objects.all()
    remedy_slug = request.GET.get('remedy')

     # اگر دسته‌ای انتخاب شده باشد → فیلتر کن
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if remedy_slug and remedy_slug != "":
        # فیلتر محصولات بر اساس رابطه ManyToMany با Remedy
        products = products.filter(remedies__slug=remedy_slug)
    
    # گرفتن تمام دسته‌بندی‌های درمانی برای نمایش در دکمه‌ها
    remedies = Remedy.objects.all()
    
    return render (request,"products/product_list.html",{"products":products,"categories":categories,'remedies': remedies,  "selected_category": category_slug})

def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True,
        available=True,
    )

    related = (Product.objects
               .filter(category=product.category, is_active=True, available=True)
               .exclude(id=product.id)
               .order_by("-created")[:6])

    return render(request, "products/product_detail.html", {
        "product": product,
        "related": related,
    })
def about_detail(request):
    return render(request,"about_detail.html")

# Create your views here.
