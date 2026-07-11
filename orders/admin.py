from django.contrib import admin
from django.utils.html import format_html
from .models import OrderRequest


@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "full_name",
        "mobile",
        "items_count",
        "order_total",
        "city",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "full_name",
        "mobile",
        "city",
        "id"
    )

    list_editable = (
        "status",
    )

    readonly_fields = (
        "created_at",
        "cart_preview",
    )

    fieldsets = (

        ("اطلاعات مشتری", {

            "fields": (

                "full_name",
                "mobile",
                "city",
                "note",
                "status",
            )
        }),

        ("اقلام سفارش", {

            "fields": (
                "cart_preview",
            )
        }),

        ("اطلاعات سیستم", {

            "fields": (
                "created_at",
                "ip_address",
                "user_agent",
                "sms_sent",
                "sms_error",
            )
        }),

    )

    def items_count(self, obj):
        return len(obj.cart_data or [])

    items_count.short_description = "تعداد کالا"

    def order_total(self, obj):

        total = 0

        for item in obj.cart_data or []:
            total += item["qty"] * item["unit_price"]

        return f"{total:,} تومان"

    order_total.short_description = "جمع سفارش"

    def cart_preview(self, obj):

        if not obj.cart_data:
            return "هیچ کالایی ثبت نشده"

        html = ""

        grand_total = 0

        for item in obj.cart_data:

            row_total = item["qty"] * item["unit_price"]

            grand_total += row_total

            html += f"""

            <div style="
                border:1px solid #ddd;
                border-radius:10px;
                padding:12px;
                margin-bottom:12px;
                background:#fafafa;
            ">

                <h3 style="margin:0;color:#198754;">
                    {item['product_name']}
                </h3>

                <div style="margin-top:8px">

                    <b>ظرف:</b>
                    {item['container_label']}

                </div>

                <div>

                    <b>تعداد:</b>
                    {item['qty']}

                </div>

                <div>

                    <b>قیمت واحد:</b>

                    {item['unit_price']:,}
                    تومان

                </div>

                <div style="margin-top:8px;color:#0d6efd">

                    <b>جمع:</b>

                    {row_total:,}
                    تومان

                </div>

            </div>

            """

        html += f"""

        <hr>

        <div style="
            font-size:18px;
            color:#198754;
        ">

        <b>

        جمع کل سفارش

        :

        {grand_total:,}
        تومان

        </b>

        </div>

        """

        return format_html(html)

    cart_preview.short_description = "جزئیات سفارش"