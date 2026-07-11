from django.urls import path
from .views import create_order_request, send_verify_code,verify_code_and_create_order

app_name = "orders"

urlpatterns = [
   path("send-code/", send_verify_code),
path("verify-code/", verify_code_and_create_order),

    path("create/", create_order_request, name="create"),
]
