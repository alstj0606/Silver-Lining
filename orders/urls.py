from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('aibot/', views.AIbot.as_view(), name='aibot'),
    path('kiosk/', views.kiosk_view, name='kiosk'),
    path('menu/', views.menu_view, name='menu'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('order_complete/<int:order_number>/', views.order_complete, name='order_complete'),
    path('start_order/', views.start_order, name='start_order'),
    path('face_recognition/', views.face_recognition, name='face_recognition'),
]
