import redis
from django_redis import get_redis_connection
from django.conf import settings
from django.core.cache import cache
import json

def redis_test(request):
    r = redis.StrictRedis.from_url(settings.CACHES['default']['LOCATION'])
    print("\n\n Pinging Redis...")
    try:
        if r.ping():
            print("\n\n Redis connection successful.")
    except redis.ConnectionError:
        print("\n\n Redis connection failed.")

    cache.set("cache", "됐으면 좋겠다")


# 장바구니 항목을 dict로 변환
class CartItem:
    def __init__(self, image, menu_name, price, quantity):
        self.image = image
        self.menu_name = menu_name
        self.price = price
        self.quantity = quantity

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "image": self.image,
            "menu_name": self.menu_name,
            "price": self.price,
            "quantity": self.quantity
        }


# 장바구니 데이터를 redis에 생성, 조회, 수정, 삭제
class Cart:
    def __init__(self, username):
        self.username = username
        self.cart_key = f"cart:{self.username}"

    # 장바구니의 현재 상태를 조회합니다.
    def get_cart(self):
        redis_conn = get_redis_connection("default")
        cart_data = redis_conn.hgetall(self.cart_key)
        return_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in cart_data.items()}
        return return_data

    # 장바구니에 메뉴를 추가합니다.
    def add_to_cart(self, item):
        redis_conn = get_redis_connection("default")
        menu_name = item['menu_name']
        quantity = item['quantity']
        price = item['price']
        image = item['image']

        item_data = json.dumps({
            'menu_name': menu_name,
            'quantity': quantity,
            'price': price,
            'image': image
        })

        redis_conn.hset(self.cart_key, menu_name, item_data)

    # 장바구니 메뉴의 수량을 수정합니다.
    def update_quantity(self, item_data):
        redis_conn = get_redis_connection("default")
        name = item_data["name"]
        price = item_data["price"]
        quantity = item_data["quantity"]
        update_data = json.dumps(item_data)
        redis_conn.hset(self.cart_key, name, update_data)

    # 메뉴를 장바구니에서 삭제합니다.
    def remove(self, menu_name):
        redis_conn = get_redis_connection("default")
        redis_conn.hdel(self.cart_key, menu_name)

    # 장바구니 전체를 삭제합니다.
    def clear(self):
        redis_conn = get_redis_connection("default")
        redis_conn.delete(self.cart_key)