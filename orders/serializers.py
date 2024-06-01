from rest_framework import serializers

class CartSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    image = serializers.ImageField()
    name = serializers.CharField(max_length=100)
    price = serializers.IntegerField()
    quantity = serializers.IntegerField()
