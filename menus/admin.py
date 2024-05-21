from django.contrib import admin
from .models import Hashtag, Menu

class HashtagAdmin(admin.ModelAdmin):
    list_display = ('hashtag', 'menu')
    search_fields = ('hashtag',)
    list_filter = ('menu',)

admin.site.register(Hashtag, HashtagAdmin)

class MenuAdmin(admin.ModelAdmin):
    list_display = ('food_name', 'price', 'store')
    search_fields = ('food_name', 'store__username')
    list_filter = ('store',)

admin.site.register(Menu, MenuAdmin)
