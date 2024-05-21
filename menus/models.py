from django.db import models
from django.conf import settings


class Hashtag(models.Model):
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, null=True, blank=True, related_name='menu_hashtags')
    hashtag = models.CharField(max_length=255)
    hashtag_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_hashtag")

    def __str__(self):
        return self.hashtag


class Menu(models.Model):
    food_name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    hashtags = models.ManyToManyField('Hashtag', related_name='menu_items')
    store = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="foods")

    def __str__(self):
        return self.food_name
