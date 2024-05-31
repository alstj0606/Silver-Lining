from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint


class Hashtag(models.Model):
    hashtag = models.CharField(max_length=255)  # 해시태그를 저장하는 필드
    hashtag_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       related_name="user_hashtag")  # 해시태그를 작성한 사용자와의 외래 키 관계

    class Meta:
        constraints = [
            UniqueConstraint(fields=['hashtag', 'hashtag_author'], name='unique_user_hashtag')
            # 사용자당 해시태그는 고유해야 함을 보장하는 제약 조건
        ]

    def __str__(self):
        return self.hashtag  # 객체를 문자열로 표시할 때 해시태그를 반환


class Menu(models.Model):
    food_name = models.CharField(max_length=100)  # 음식 이름을 저장하는 필드
    price = models.PositiveIntegerField()  # 음식 가격을 저장하는 필드 (양수만 허용)
    hashtags = models.ManyToManyField('Hashtag', related_name='menu_items')  # 음식과 관련된 해시태그를 나타내는 다대다 관계
    store = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="foods")  # 음식을 등록한 가게와의 외래 키 관계
    img = models.ImageField(upload_to='menu_images/', null=True, blank=True)  # 음식 이미지를 저장하는 필드 (선택 사항)

    def __str__(self):
        return self.food_name  # 객체를 문자열로 표시할 때 음식 이름을 반환
