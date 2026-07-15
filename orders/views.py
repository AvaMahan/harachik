import requests 
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from products.models import Product,ProductContainerPrice
from django.conf import settings
from .models import OrderRequest
import threading
import random
import json
from django.views.decorators.http import require_POST

from .models import PhoneVerification 
from django.utils import timezone
from datetime import timedelta
from .sms import (
    send_verify_sms,
    send_sms_async
)

def generate_code():
    return str(random.randint(10000, 99999))

# ارسال کد

@require_POST
def send_verify_code(request):

    mobile = (
        request.POST.get("mobile") 
        or ""
    ).strip()


    if not mobile:

        return JsonResponse({
            "ok":False,
            "error":"شماره موبایل وارد نشده"
        })


    if len(mobile) != 11 or not mobile.startswith("09"):

        return JsonResponse({
            "ok":False,
            "error":"شماره موبایل معتبر نیست"
        })


    # ==========================
    # محدودیت ارسال مجدد
    # ==========================

    last_verification = PhoneVerification.objects.filter(
        mobile=mobile
    ).order_by(
        "-created_at"
    ).first()


    if last_verification:


        diff = timezone.now() - last_verification.created_at


        if diff < timedelta(seconds=60):

            remain = 60 - diff.seconds


            return JsonResponse({

                "ok":False,

                "error":
                f"لطفا {remain} ثانیه صبر کنید"

            })


    # ==========================
    # ساخت کد جدید
    # ==========================

    code = generate_code()



    # ==========================
    # باطل کردن کدهای قبلی
    # ==========================

    PhoneVerification.objects.filter(
        mobile=mobile,
        is_verified=False
    ).update(
        is_verified=True
    )



    # ==========================
    # ذخیره OTP جدید
    # ==========================

    PhoneVerification.objects.create(

        mobile=mobile,

        code=code

    )



    # ==========================
    # ارسال پیامک الگو
    # ==========================

    response = send_verify_sms(
        mobile,
        code
    )


    if not response:


        return JsonResponse({

            "ok":False,

            "error":"خطا در ارسال پیامک"

        })



    print(
        "OTP RESPONSE:",
        response.text
    )



    return JsonResponse({

        "ok":True

    })



@require_POST
def verify_code_and_create_order(request):
   
    mobile = (request.POST.get("mobile") or "").strip()
    code = (request.POST.get("code") or "").strip()

    if not mobile or not code:
        return JsonResponse({
            "ok": False,
            "error": "اطلاعات ناقص است"
        }, status=400)

    verification = PhoneVerification.objects.filter(
    mobile=mobile,
    code=code,
    is_verified=False
).order_by(
    "-created_at"
).first()

    if not verification:
        return JsonResponse({
            "ok": False,
            "error": "کد تایید اشتباه است"
        })

    if verification.is_expired():
        return JsonResponse({
            "ok": False,
            "error": "کد منقضی شده"
        })

    verification.is_verified = True
    verification.save()

    # ✅ این خط قبلاً وجود نداشت
    return JsonResponse({
        "ok": True
    })


def create_order_request(request):
   


    full_name = (request.POST.get("full_name") or "").strip()
    mobile = (request.POST.get("mobile") or "").strip()
  
    order_type = (request.POST.get("order_type") or "single_yazd").strip()
    city = (request.POST.get("city") or "").strip()
    note = (request.POST.get("note") or "").strip()
    cart_raw = request.POST.get("cart", "[]")
    try:
        cart_data = json.loads(cart_raw)
    except Exception:
        cart_data = []
    

    if not full_name:
        return JsonResponse({"ok": False, "error": "نام را وارد کنید."}, status=400)
    if not mobile:
        return JsonResponse({"ok": False, "error": "موبایل را وارد کنید."}, status=400)
    if not cart_data:
        return JsonResponse({
        "ok": False,
        "error": "سبد خرید خالی است"
    })
    

 


    order = OrderRequest.objects.create(
        full_name=full_name,
        mobile=mobile,
        city=city,
        note=note,
        cart_data=cart_data,
   
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=(request.META.get("HTTP_USER_AGENT", "")[:255]),
    )

    send_sms_async(mobile, order.id, full_name)

    return JsonResponse({"ok": True, "id": order.id})

# Create your views here.
