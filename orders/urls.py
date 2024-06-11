from django.urls import path
from . import views



app_name = 'orders'

urlpatterns = [
    path('start_order/', views.start_order, name='start_order'),  # 맨 처음 주문을 위해 얼굴인식 버튼을 띄어주는 템플릿
    path('face_recognition/', views.face_recognition, name='face_recognition'),  # 얼굴인식 함수
    path('elder_start/', views.elder_start, name='elder_start'),  # 고연령자 템플릿 음성인식
    path('elder_menu/', views.elder_menu, name='elder_menu'),  # 고연령자 템플릿 추천 메뉴
    path('menu/', views.menu_view, name='menu'),  # 일반 키오스크 템플릿 render
    path("switch-language/", views.switch_language, name="switch-language"),  # 언어 변경 함수
    path('aibot/', views.AIbot.as_view(), name='aibot'),  # AI음성인식으로 답변 및 추천 메뉴 선정
    path('get_menus/', views.MenusAPI.as_view(), name='get_menus'),  # 데이터베이스에서 메뉴 목록을 조회 가져오는 API
    path('order_complete/<int:order_number>/', views.order_complete, name='order_complete'),  # 주문완료 후 주문 번호 알려주는 함수
    path('orderbot/', views.orderbot.as_view(), name="orderbot"),  # 고령자 탬플릿 조건 인식 구분 봇
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),
    path("cart/remove/<str:menu_name>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("cart/update/", views.add_quantity, name="add_quantity"),
    path("submit/", views.submit_order, name="submit_order"),
    path('dashboard/', views.orders_dashboard_view, name='orders_dashboard_view'),
    path('dashboard/orders_dashboard_data/', views.orders_dashboard_data, name='orders_dashboard_data'),

]

