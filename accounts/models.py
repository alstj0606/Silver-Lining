from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    CATEGORY_CHOICES = (
        ("CH", "치킨"),
        ("CA", "카페"),
    )

    store_name = models.CharField(max_length=100)
    tel = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=100)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
