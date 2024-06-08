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

class Cart:
    def __init__(self, username):
        self.username = username
        self.cart_key = f"cart:{self.username}" 


## **Fetching Cart Data**:
    def get_cart(self):
        redis_conn = get_redis_connection("default")
        cart_data = redis_conn.hgetall(self.cart_key)
        print("\n\n cart_data를 넘겨주어야 하는데 어떻게 생겼나:", cart_data)
        return_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in cart_data.items()}
        print("\n\n 그래서 넘어갈 때는 어떻게 생긴채로 넘어가나: ", return_data)
        return return_data

## **Adding an Item to the Cart**:
    def add_to_cart(self, item):
        redis_conn = get_redis_connection("default")
        print("\n\n item이 어떻게 들어왔는지 : ", item)
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
        print("\n\n item_data 는 잘 들어온건지 >>>> ", item_data)
        print("\n\n type menu_name >>", type(menu_name))
        print("\n\n item_data type", type(item_data))
        redis_conn.hset(self.cart_key, menu_name, item_data)
        print("\n\n\n redis에 저장이 잘 됐는지: ", self.cart_key, menu_name, item_data)


## **Removing an Item**:
    def remove(self, menu_name):
        print("\n\n menu_name: ", menu_name)
        redis_conn = get_redis_connection("default")
        redis_conn.hdel(self.cart_key, menu_name)

## Clear the cart
    def clear(self):
        redis_conn = get_redis_connection("default")
        redis_conn.delete(self.cart_key)
        print("\n\n cart.py의 clear>>>>>>>>>", self.cart_key)
        return "clear다녀감.."


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