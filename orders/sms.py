
import threading

import requests
from django.conf import settings
from .models import OrderRequest


def send_verify_sms(mobile, code):

    url = "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber"

    try:
        response = requests.post(
            url,
            data={
                "username": settings.SMS_USERNAME,
                "password": settings.SMS_APIKEY,
                "to": mobile,
                "from": settings.SMS_LINE,
                "text": code,
                "bodyId": settings.SMS_BODY_ID,
            },
            timeout=10
        )

        print("OTP RESPONSE:", response.text)

        return response

    except Exception as e:
        print("OTP ERROR:", e)
        return None

def send_sms_notification(mobile, order_id, full_name):

    username = settings.SMS_USERNAME
    password = settings.SMS_APIKEY
    my_line = settings.SMS_LINE


    # پیام مشتری (الگو)
    customer_url = (
        "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber"
    )


    # پیام ادمین (عادی)
    admin_url = (
        "https://rest.payamak-panel.com/api/SendSMS/SendSMS"
    )


    try:


        # =====================
        # پیام مشتری با الگو
        # =====================

        user_response = requests.post(

            customer_url,

            data={

                "username": username,

                "password": password,

                "to": mobile,

                "from": my_line,

                "text": full_name,

                "bodyId": settings.SMS_ORDER_BODY_ID,

            },

            timeout=10
        )


        print(
            "CUSTOMER SMS:",
            user_response.text
        )



        # =====================
        # پیام ادمین
        # =====================

        admin_text = (
            f"سفارش جدید ثبت شد!\n"
            f"نام: {full_name}\n"
            f"کد سفارش: {order_id}"
        )


        admin_response = requests.post(

            admin_url,

            data={

                "username": username,

                "password": password,

                "to": "09134590122",

                "from": my_line,

                "text": admin_text,

            },

            timeout=10
        )


        print(
            "ADMIN SMS:",
            admin_response.text
        )



        # ثبت وضعیت ارسال

        if "RetStatus\":1" in user_response.text:

            OrderRequest.objects.filter(
                id=order_id
            ).update(
                sms_sent=True
            )

        else:

            OrderRequest.objects.filter(
                id=order_id
            ).update(
                sms_error=user_response.text
            )


    except Exception as e:

        print(
            "SMS ERROR:",
            e
        )

def send_sms_async(mobile, order_id, full_name):
    thread = threading.Thread(
        target=send_sms_notification,
        args=(mobile, order_id, full_name),
    )
    thread.daemon =False
    thread.start()   


import threading

import requests
from django.conf import settings
from .models import OrderRequest


def send_verify_sms(mobile, code):

    url = "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber"

    try:
        response = requests.post(
            url,
            data={
                "username": settings.SMS_USERNAME,
                "password": settings.SMS_APIKEY,
                "to": mobile,
                "from": settings.SMS_LINE,
                "text": code,
                "bodyId": settings.SMS_BODY_ID,
            },
            timeout=10
        )

        print("OTP RESPONSE:", response.text)

        return response

    except Exception as e:
        print("OTP ERROR:", e)
        return None

def send_sms_notification(mobile, order_id, full_name):

    username = settings.SMS_USERNAME
    password = settings.SMS_APIKEY
    my_line = settings.SMS_LINE


    # پیام مشتری (الگو)
    customer_url = (
        "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber"
    )


    # پیام ادمین (عادی)
    admin_url = (
        "https://rest.payamak-panel.com/api/SendSMS/SendSMS"
    )


    try:


        # =====================
        # پیام مشتری با الگو
        # =====================

        user_response = requests.post(

            customer_url,

            data={

                "username": username,

                "password": password,

                "to": mobile,

                "from": my_line,

                "text": full_name,

                "bodyId": settings.SMS_ORDER_BODY_ID,

            },

            timeout=10
        )


        print(
            "CUSTOMER SMS:",
            user_response.text
        )



        # =====================
        # پیام ادمین
        # =====================

        admin_text = (
            f"سفارش جدید ثبت شد!\n"
            f"نام: {full_name}\n"
            f"کد سفارش: {order_id}"
        )


        admin_response = requests.post(

            admin_url,

            data={

                "username": username,

                "password": password,

                "to": "09134590122",

                "from": my_line,

                "text": admin_text,

            },

            timeout=10
        )


        print(
            "ADMIN SMS:",
            admin_response.text
        )



        # ثبت وضعیت ارسال

        if "RetStatus\":1" in user_response.text:

            OrderRequest.objects.filter(
                id=order_id
            ).update(
                sms_sent=True
            )

        else:

            OrderRequest.objects.filter(
                id=order_id
            ).update(
                sms_error=user_response.text
            )


    except Exception as e:

        print(
            "SMS ERROR:",
            e
        )

def send_sms_async(mobile, order_id, full_name):
    thread = threading.Thread(
        target=send_sms_notification,
        args=(mobile, order_id, full_name),
    )
    thread.daemon =False
    thread.start()   

