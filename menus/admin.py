from django.contrib import admin
from .models import Hashtag, Menu


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    readonly_fields = ("store", "store_id")
    list_display = ("food_name", "price", "get_hashtags")
    search_fields = ("food_name", "price")

    # list_filter = ("hashtags",)
    # date_hierarchy = "created_at"
    # ordering = ("-created_at",)

    def get_form(self, request, obj, **kwargs):
        form = super(MenuAdmin, self).get_form(request, obj, **kwargs)
        # print("form>>>>>>>>>>>", form)
        # print("dir>>>>>>>>>>>>>>>", dir(form))  #### 내부를 볼 수 있음..!!
        # print("base_fields >>>>>>>>>> ", form.base_fields)
        if request.user.is_superuser:
            form.base_fields['hashtags'].queryset = Hashtag.objects.all()
        elif request.user.is_staff:
            form.base_fields['hashtags'].queryset = Hashtag.objects.filter(hashtag_author_id=request.user)
        return form

    def save_model(self, request, obj, form, change):
        obj.store = request.user
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

    def get_hashtags(self, obj):
        return ", ".join([hashtag.hashtag for hashtag in obj.hashtags.all()])

    get_hashtags.short_description = "Hashtags"


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    readonly_fields = ("hashtag_author",)
    list_display = ("hashtag", "hashtag_author", "get_menus")
    list_filter = ("hashtag_author",)

    def save_model(self, request, obj, form, change):
        obj.hashtag_author = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(hashtag_author=request.user)

    def get_menus(self, obj):
        return ", ".join([menu.food_name for menu in obj.menu_items.all()])

    get_menus.short_description = "Menus"
