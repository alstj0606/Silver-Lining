from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint


class Hashtag(models.Model):
    hashtag = models.CharField(max_length=255)
    hashtag_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_hashtag")

    class Meta:
        constraints = [
            UniqueConstraint(fields=['hashtag', 'hashtag_author'], name='unique_user_hashtag')
        ]

    def __str__(self):
        return self.hashtag


class Menu(models.Model):
    food_name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    hashtags = models.ManyToManyField('Hashtag', related_name='menu_items')
    store = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="foods")

    def __str__(self):
        return self.food_name
