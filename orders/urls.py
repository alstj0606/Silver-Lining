from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('aibot/', views.AIbot.as_view(), name='aibot'),
    path('menu/', views.menu_view, name='menu'),
    path('menu_big/', views.menu_view_big, name='menu_big'),
    path('get_menus/', views.MenusAPI.as_view(), name='get_menus'),
    path('order_complete/<int:order_number>/', views.order_complete, name='order_complete'),
    path('start_order/', views.start_order, name='start_order'),
    path('face_recognition/', views.face_recognition, name='face_recognition'),
]
