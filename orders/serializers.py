from rest_framework import serializers


class CartSerializer(serializers.Serializer):
    image = serializers.ImageField()
    menu_name = serializers.CharField(max_length=100)
    price = serializers.IntegerField()
    quantity = serializers.IntegerField()
