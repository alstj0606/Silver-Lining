from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'username', 'password1', 'password2', 'email', 'is_superuser', 'is_staff', 'store_name', 'tel', 'address',
            'category'),
        }),
    )


# admin에 User 모델 등록
admin.site.register(User, CustomUserAdmin)
