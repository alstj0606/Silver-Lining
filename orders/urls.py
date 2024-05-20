from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('input/', views.AIbot.as_view(), name='AIbot'),
    path('kiosk/', views.kiosk_view, name='kiosk'),
]