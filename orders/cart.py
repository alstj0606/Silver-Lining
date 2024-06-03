import redis
from django_redis import get_redis_connection
from django.conf import settings
from django.core.cache import cache
import json

# # Redis 연결 설정
# r = redis.StrictRedis.from_url(settings.CACHES['default']['LOCATION'])

def redis_test(request):
    r = redis.StrictRedis.from_url(settings.CACHES['default']['LOCATION'])
    print("\n\n Pinging Redis...")
    try:
        if r.ping():
            print("\n\n Redis connection successful.")
    except redis.ConnectionError:
        print("\n\n Redis connection failed.")

    cache.set("cache", "됐으면 좋겠다")
    

class CartItem:
    def __init__(self, image, name, price, quantity):
        self.image = image
        self.name = name
        self.price = price
        self.quantity = quantity

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "image": self.image,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity
        }

class Cart:
    def __init__(self, username):
        self.username = username
        self.cart_key = f"cart:{self.username}" # 문자열 오늘의날짜 _> 오늘의날짜+ordernumber
        # 아메리카노 한 개 누름 -> cart key 240601 
        # cart key 240601 -> 아메리카노 0 개 ->
        # 현재 장바구니만 cartkey로 불러오고
        # 주문 확정 +오더넘버
        # 단점: 키오스크 한 대에서만 가능

        # cart_key : mega 광화문점
        # mega --> 장바구니 mega 광화문점 한 대만 있어야 함

## **Adding an Item to the Cart**:
    def add_to_cart(self, item):
        redis_conn = get_redis_connection("default")
        print("\n\n item이 어떻게 들어왔는지 : ", item)
        menu_name = item['name']
        quantity = item['quantity']
        price = item['price']
        image = item['image']

        item_data = json.dumps({
            'quantity': quantity,
            'price': price,
            'image': image
        })

        redis_conn.hset(self.cart_key, menu_name, item_data)
        print("\n\n\n redis에 저장이 잘 됐는지: ")

## **Updating Quantity**:
    def update_quantity(self, item_data):
        redis_conn = get_redis_connection("default")
        # dict 형식으로 받는다 : item_data {}
        # "name"으로 해당 데이터 불러오고 "quantity"로 해당 value를 수정 ? 
        # 이렇게 해서 hset 으로 저장하나?
        print("\n\n item_data 잘 넘어왔나: ", item_data)
        name = item_data["name"]
        print("\n\n name >>> ", name)
        update_data = json.dumps(item_data)
        redis_conn.hset(self.cart_key, name, update_data)

        # name = key, quantity =value
        # hincrby 로 quantity 수정
        # 해당 name의 quantity가 수정된 채로 저장됨

        # value = redis_conn.hget(self.cart_key, name)
        # print("\n\n value : ", value)
        # quantity_key = value # byte indices must be integers or slices, not str
        # print("\n\n name으로 value 불러오기+quantity: ", quantity_key)
        # redis_conn.hincrby(self.cart_key, quantity_key, quantity)
        # # 값을 덮어씌우려면 그냥 hset으로 저장하는 것이..!!


## **Removing an Item**:
    def remove(self, menu_name):
        print("\n\n menu_name: ", menu_name)
        redis_conn = get_redis_connection("default")
        redis_conn.hdel(self.cart_key, menu_name)

## Clear the cart
    def clear(self):
        redis_conn = get_redis_connection("default")
        redis_conn.delete(self.cart_key)

## **Fetching Cart Data**:

    def get_cart(self):
        redis_conn = get_redis_connection("default")
        cart_data = redis_conn.hgetall(self.cart_key)
        return {k.decode('utf-8'): v.decode('utf-8') for k, v in cart_data.items()}

    # # 항목 추가
    # def add(self, item):
    #     cart = self.get_cart()
    #     cart[item.item_id] = item.to_dict()
    #     r.setex(self.cart_key, settings.CACHE_TTL, json.dumps(cart)) 

    # # 값이 들어간 시점으로부터 지정 캐싱 시간 동안 살아있음
    # # 값을 수정했을 때 수정 시점으로부터 캐싱 시간이 새롭게 늘어나는 것이 아님


    # # 장바구니 가져오기
    # def get_cart(self):
    #     cart_data = r.get(self.cart_key)
    #     if cart_data:
    #         return json.loads(cart_data)
    #     return {}

    # # 항목 제거
    # def remove(self, item_id):
    #     cart = self.get_cart()
    #     if item_id in cart:
    #         del cart[item_id]
    #         r.setex(self.cart_key, settings.CACHE_TTL, json.dumps(cart))

    # 전체 장바구니 삭제
    # def clear(self):
    #     r.delete(self.cart_key)

    #     # 결제하기 누르면 order 테이블 보내서 저장
    #     # clear()를 작동시켜서 장바구니 캐시를 모두 삭제해준다.