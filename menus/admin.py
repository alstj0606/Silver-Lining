from django.contrib import admin
from .models import Hashtag, Menu


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    readonly_fields = ("store", "store_id")
    list_display = ("food_name", "price")
    search_fields = ("food_name", "price")
    # list_filter = ("name", "user")
    # date_hierarchy = "created_at"
    # ordering = ("-created_at",)

    def get_form(self, request, obj, **kwargs):
        form = super(MenuAdmin, self).get_form(request, obj, **kwargs)
        print("form>>>>>>>>>>>", form)
        print("dir>>>>>>>>>>>>>>>", dir(form)) #### 내부를 볼 수 있음..!!
        print("base_fields >>>>>>>>>> ", form.base_fields) 
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
    

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    readonly_fields = ("menu_id", "menu", "hashtag_author")

    def get_search_results(self, request, queryset, search_term):
        print("get_search_results >>>>>>>> 들어오는지")
        queryset = queryset.filter(hashtag_author_id=request.user)
        qs = super().get_search_results(request, queryset, search_term)
        print(qs)
        return qs

    def save_model(self, request, obj, form, change):
        obj.hashtag_author = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(hashtag_author_id=request.user)
