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

def generate_code():
    return str(random.randint(10000, 99999))

def send_verify_sms(mobile, code):

    username = settings.SMS_USERNAME
    password = settings.SMS_APIKEY
    my_line = settings.SMS_LINE

    url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"

    text = f"کد تایید هراجیک: {code}"

    try:

        requests.post(
            url,
            data={
                "username": username,
                "password": password,
                "to": [mobile],
                "from": my_line,
                "text": text,
            },
            timeout=10
        )

    except Exception as e:
        print("OTP SMS ERROR:", e)



def send_sms_notification(mobile, order_id, full_name):

    username = settings.SMS_USERNAME
    password = settings.SMS_APIKEY
    my_line = settings.SMS_LINE
    

    url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"

    user_text = f"هراچیک؛ {full_name} عزیز، سفارش شما ثبت شد. به‌زودی با شما تماس می‌گیریم."

    admin_text = f"سفارش جدید ثبت شد!\nنام: {full_name}\nکد سفارش: {order_id}"

    try:
        user_response = requests.post(
            url,
            data={
                "username": username,
                "password": password,
                "to":[mobile] ,
                "from": my_line,
                "text": user_text,
              
            },
            timeout=10
        )

        print("USER SMS:", user_response.text)

        admin_response = requests.post(
            url,
            data={
                "username": username,
                "password": password,
                "to": ["09134590122"],
                "from": my_line,
                "text": admin_text,
                
            },
            timeout=10
        )
        if "RetStatus\":1" in user_response.text:
            OrderRequest.objects.filter(id=order_id).update(sms_sent=True)
        else:
            OrderRequest.objects.filter(id=order_id).update(
            sms_error=user_response.text
        )

        print("ADMIN SMS:", admin_response.text)
    except Exception as e:
        print("SMS Error:", e)

def send_sms_async(mobile, order_id, full_name):
    thread = threading.Thread(
        target=send_sms_notification,
        args=(mobile, order_id, full_name),
    )
    thread.daemon = True
    thread.start()




# ارسال کد

@require_POST

def send_verify_code(request):
    mobile = (request.POST.get("mobile") or "").strip()

    if not mobile:
        return JsonResponse({"ok": False, "error": "شماره موبایل وارد نشده"})

    if len(mobile) != 11 or not mobile.startswith("09"):
        return JsonResponse({"ok": False, "error": "شماره موبایل معتبر نیست"})

    code = generate_code()
    PhoneVerification.objects.create(mobile=mobile, code=code)

    username = settings.SMS_USERNAME
    password = settings.SMS_APIKEY
    my_line = settings.SMS_LINE
    url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"
    text = f"کد تایید هراجیک: {code}"

    try:
        response = requests.post(
            url,
            data={
                "username": username,
                "password": password,
                "to": [mobile],
                "from": my_line,
                "text": text,
            },
            timeout=10
        )

        print("SEND OTP RESPONSE:", response.text)
        

        if response.status_code != 200:
            return JsonResponse({
                "ok": False,
                "error": "ارسال پیامک ناموفق بود"
            }, status=500)

        return JsonResponse({"ok": True})

    except Exception as e:
        print("SEND OTP ERROR:", e)
        return JsonResponse({
            "ok": False,
            "error": "خطا در ارسال پیامک"
        }, status=500)



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
    ).last()

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
