from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('aibot/', views.AIbot.as_view(), name='aibot'),
    path('kiosk/', views.kiosk_view, name='kiosk'),
]