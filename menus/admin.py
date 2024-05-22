
from django.contrib import admin
from .models import Hashtag, Menu

# class CustomListFilterA(admin.SimpleListFilter):
#     title = _("hashtag")
#     parameter_name = "hashtag"

#     def lookups(self, request, model_admin):
#             """
#             Returns a list of tuples. The first element in each
#             tuple is the coded value for the option that will
#             appear in the URL query. The second element is the
#             human-readable name for the option that will appear
#             in the right sidebar.
#             """
#             return [
#                 ("80s", _("in the eighties")),
#                 ("90s", _("in the nineties")),
#             ]

#     def queryset(self, request, queryset):
#         """
#         Returns the filtered queryset based on the value
#         provided in the query string and retrievable via
#         `self.value()`.
#         """
#         # Compare the requested value (either '80s' or '90s')
#         # to decide how to filter the queryset.
#         if self.value() == "80s":
#             return queryset.filter(
#                 birthday__gte=date(1980, 1, 1),
#                 birthday__lte=date(1989, 12, 31),
#             )
#         if self.value() == "90s":
#             return queryset.filter(
#                 birthday__gte=date(1990, 1, 1),
#                 birthday__lte=date(1999, 12, 31),
#             )


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
                list_filter = [
        ("hashtags", admin.RelatedOnlyFieldListFilter),
    ]
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


##admin page내에서 filter
##admin계정 -> menu: store별로, hastag: hashtag_author별로
##staff계정 -> menu:카테고리? , hashtag: 메뉴별로?