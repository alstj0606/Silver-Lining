from django.apps import AppConfig
from modeltranslation.decorators import register


class MenusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # 기본 자동 필드를 설정합니다.
    name = 'menus'  # 앱의 이름을 지정합니다.

    def ready(self):
        # 이 시점에서 모델이 로드되었으므로 모델에 대한 번역 옵션을 설정합니다.
        from modeltranslation.translator import translator, TranslationOptions
        from .models import Hashtag, Menu

        # Hashtag 모델에 대한 번역 옵션을 등록합니다.
        @register(Hashtag)
        class HashtagTranslationOptions(TranslationOptions):
            fields = ('hashtag',)  # 번역할 필드를 지정합니다.

        # Menu 모델에 대한 번역 옵션을 등록합니다.
        @register(Menu)
        class MenuTranslationOptions(TranslationOptions):
            fields = ('food_name',)  # 번역할 필드를 지정합니다.
