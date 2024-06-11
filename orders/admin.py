from django.contrib import admin
from .models import Order
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from django.urls import path
from django.shortcuts import redirect
# from .views import orders_dashboard
from django.template.response import TemplateResponse

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ("store", "created_at", "total_price")  # 읽기 전용 필드 설정
    list_display = (
    "order_number", "created_at", "status", "store", "display_order_menu", "total_price")  # 관리자 페이지 목록에 표시할 필드 설정
    search_fields = ("order_number", "status")  # 검색 필드 설정
    list_filter = (
        "status",
        ("created_at", DateRangeFilter),  # DateRangeFilter를 사용하여 기간별 필터링 추가
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store=request.user)

    def save_model(self, request, obj, form, change):
        obj.store = request.user
        super().save_model(request, obj, form, change)

    def display_order_menu(self, obj):
        try:
            order_details = ", ".join(
                [f"{item.get('food_name_ko', 'N/A')}({item.get('count', 'N/A')})" for item in obj.order_menu])
            return order_details
        except KeyError:
            return "Invalid order menu format"

    display_order_menu.short_description = "Order Menu"

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ["status", "store", "created_at", ("created_at", DateRangeFilter)]
        return ["status", "created_at", ("created_at", DateRangeFilter)]


class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view))
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        return redirect('/orders/dashboard/')

admin_site = CustomAdminSite(name='custom_admin')

admin_site.register(Order)