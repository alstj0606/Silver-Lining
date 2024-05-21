from django.contrib import admin
from .models import Hashtag, Menu

admin.site.register(Hashtag)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    readonly_fields = ("store", "store_id")
    list_display = ("food_name", "price")
    search_fields = ("food_name", "price")
    # list_filter = ("name", "user")
    # date_hierarchy = "created_at"
    # ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):
        obj.store = request.user
        # store_id = obj.store.store_name
        # obj.store.store_id = request.user.id
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store_id=request.user)
    
    def get_list_filter(self, request):
        if request.user.is_superuser:
            list_filter = ("store_id",)
        else:
            list_filter = ("hashtags",)
        return list_filter