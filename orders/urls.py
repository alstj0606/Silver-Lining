from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('aibot/', views.AIbot.as_view(), name='aibot'),
    path('menu/', views.menu_view, name='menu'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('order_complete/<int:order_number>/', views.order_complete, name='order_complete'),
]
