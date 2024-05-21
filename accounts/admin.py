from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'store_name', 'tel', 'address', 'category')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'store_name', 'tel', 'address', 'category', 'is_active', 'is_staff')}
        ),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'store_name', 'tel', 'address', 'category', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'store_name', 'tel', 'address', 'category')
    ordering = ('username',)

admin.site.register(User, CustomUserAdmin)
