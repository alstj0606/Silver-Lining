from django.contrib import admin
from .models import Hashtag, Menu


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    readonly_fields = ("store", "store_id")  # 읽기 전용 필드 설정
    list_display = ("food_name", "price", "get_hashtags")  # 관리자 페이지 목록에 표시할 필드 설정
    search_fields = ("food_name", "price")  # 검색 필드 설정

    def get_form(self, request, obj, **kwargs):
        form = super(MenuAdmin, self).get_form(request, obj, **kwargs)

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
            list_filter = [
                ("hashtags", admin.RelatedOnlyFieldListFilter),
            ]
        return list_filter

    def get_hashtags(self, obj):
        return ", ".join([hashtag.hashtag for hashtag in obj.hashtags.all()])

    get_hashtags.short_description = "Hashtags"


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    readonly_fields = ("hashtag_author",)  # 읽기 전용 필드 설정
    list_display = ("hashtag", "hashtag_author", "get_menus")  # 관리자 페이지 목록에 표시할 필드 설정

    # list_filter = ("hashtag_author",)

    def save_model(self, request, obj, form, change):
        obj.hashtag_author = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(hashtag_author=request.user)

    def get_list_display(self, request):
        if request.user.is_superuser:
            list_display = ("hashtag", "hashtag_author", "get_menus")
        else:
            list_display = ("hashtag", "get_menus")
        return list_display

    def get_list_filter(self, request):
        if request.user.is_superuser:
            list_filter = ("hashtag_author",)
        else:
            list_filter = ()
        return list_filter

    def get_menus(self, obj):
        return ", ".join([menu.food_name for menu in obj.menu_items.all()])

    get_menus.short_description = "Menus"
