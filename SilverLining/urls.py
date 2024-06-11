"""
URL configuration for SilverLining project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.db import connection
from orders import views
from orders.admin import CustomAdminSite



def dummy_favicon(request):
    return HttpResponse(status=204)


def health_check(request):
    # 데이터베이스 연결 상태 확인
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
    except Exception as e:
        # 데이터베이스 연결 실패 시 500 에러 반환
        return HttpResponse(status=500)

    # 데이터베이스 연결 성공 시 "OK" 응답 반환
    return HttpResponse("OK")


urlpatterns = [
    path('health_check/', health_check),
    path('', views.main_page, name='mainpage'),  # 맨 처음으로 나오게 될 페이지
    path('', include('admin_volt.urls')),  # admin_page theme
    path('admin/', admin.site.urls),
    path('orders/', include('orders.urls')),
    path('favicon.ico', dummy_favicon),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
