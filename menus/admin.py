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
    

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    readonly_fields = ("menu_id", "menu", "hashtag_author")

    # def get_queryset(self, request):
    #     print("들어오는 REQUEST >>>>>> ", request)
    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     return qs.filter(menu_id=request.user)
    
    # def get_list_filter(self, request):
    #     if request.user.is_superuser:
    #         list_filter = ("menu_id",)
    #     else:
    #         list_filter = ("hashtags",)
    #     return list_filter
    

## hashtag 는 menu_id 가 필요 -> 해당 menu를 작성한 유저만 해시태그를 조회할 수 있도록 해야함
## hashtag -> menu -> user. 메뉴는 유저마다 다르기 때문에 요청한 유저만 자신이 작성한 해시태그를 CRUD 가능




#### hashtag 만들 때 반드시 메뉴가 있어야 하나? -> 해시태그를 미리 만들어 놓고 메뉴를 생성할 때 선택하게
#### 메뉴를 생성할 때는 해시태그 필수 -> 음성인식이 가능하도록


#### add menu 할 때 태그까지 선택해서 넣기
#### hashtag 입력할 때 menu를 dropdown으로 선택하기

### 1. menu를 blank=True
### 2. menu와 연관된 User 모델.. Hashtag - User : 해시태그를 만든 유저. 가 될 것. 
### 3. User 1 - 커피 라는 해시태그, User2 - 커피 라는 해시태그를 만들 때 같은 커피로 인식이 되나 ?
### 지금 pk, menu, hashtag -> 작성한 사람 X: