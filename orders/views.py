import json

from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings  # SilverLining 앱의 설정에서 OPEN_API_KEY를 가져옵니다.
from menus.models import Menu, Hashtag  # Menu와 Hashtag 모델을 가져옵니다.
from .bot import bot, face  # AI 봇 기능을 처리하는 함수를 가져옵니다.
from .models import Order  # 주문 모델을 가져옵니다.
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # 페이지네이션을 위한 라이브러리들을 가져옵니다.
from django.utils.decorators import method_decorator  # 데코레이터를 사용하기 위한 라이브러리를 가져옵니다.
from django.utils import translation  # Django의 다국어 지원을 위한 translation 모듈을 가져옵니다.
from django.http import JsonResponse

from .orderbot import request_type, cart_ai
from .cart import CartItem, Cart, redis_test
from .serializers import CartSerializer

from rest_framework.decorators import api_view
import plotly.express as px
import pandas as pd

# 언어를 변경하는 함수입니다.
def switch_language(request):
    lang = request.GET.get('lang', settings.LANGUAGE_CODE)
    if lang:
        # 언어 변경
        translation.activate(lang)
        # 언어 쿠키 설정
        response = redirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response
    return redirect(request.META.get('HTTP_REFERER', '/'))


def main_page(requset):
    return render(requset, 'orders/mainpage.html')


# 주문을 시작하는 페이지를 렌더링합니다.
def start_order(request):
    return render(request, 'orders/start_order.html')


# 메뉴를 보여주는 페이지를 렌더링합니다.
def menu_view(request):
    return render(request, 'orders/menu.html')


# 어르신을 위한 탬플릿 뷰
def elder_start(request):
    return render(request, "orders/elder_start.html")


def elder_menu(request):
    return render(request, "orders/elder_menu.html")


# 주문이 완료된 페이지를 렌더링하며 주문 번호를 표시합니다.
def order_complete(request, order_number):
    context = {
        'order_number': order_number,
    }
    return render(request, 'orders/order_complete.html', context)


# AIbot이 요청을 받아들여 메시지를 처리하고 응답을 반환합니다.
class AIbot(APIView):
    @staticmethod
    def get(request):
        # GET 요청을 처리하는 메소드입니다.
        # 추천 메뉴를 반환합니다.
        user = request.user
        recommended_menu = request.GET.get('recommended_menu', '[]')
        # JSON 문자열을 파싱하여 리스트로 변환
        recommended_menu = json.loads(recommended_menu)
        # 현재 사용자가 작성한 모든 메뉴의 store를 가져옵니다.
        user_menus = Menu.objects.filter(store=user)
        # 추천 메뉴를 가져옵니다.
        recommended_list = []
        for recommend in recommended_menu:
            menus = user_menus.filter(food_name=recommend)
            for menu in menus:
                recommended_list.append({
                    "food_name_ko": getattr(menu, 'food_name_ko', ''),
                    "food_name": menu.food_name,
                    "price": menu.price,
                    "img_url": menu.img.url
                })

        return Response({'recommends': recommended_list})

    @staticmethod
    def post(request):
        # POST 요청을 처리하는 메소드입니다.
        # AI 봇에게 입력된 텍스트를 전달하고 응답을 받습니다.
        input_text = request.data.get('inputText')
        current_user = request.user
        message, recommended_menu = bot(input_text, current_user)
        return Response({'responseText': message, 'recommended_menu': recommended_menu})


# 메뉴 API를 제공하며 페이징된 메뉴 목록을 반환합니다.
class MenusAPI(APIView):
    # 메뉴를 페이징하여 반환합니다.
    @staticmethod
    def get_paginator(menus, page_number):
        paginator = Paginator(menus, 6)  # 페이지 당 6개의 메뉴

        try:
            menus = paginator.page(page_number)
        except PageNotAnInteger:
            menus = paginator.page(1)
        except EmptyPage:
            menus = paginator.page(paginator.num_pages)
        # 메뉴를 JSON 형식으로 변환합니다.
        menu_list = [
            {
                "food_name_ko": getattr(menu, 'food_name_ko', ''),
                'food_name': menu.food_name,
                'price': menu.price,
                'img_url': menu.img.url if menu.img else ''
            } for menu in menus
        ]
        # 전체 페이지 수를 가져옵니다.
        total_pages = paginator.num_pages
        return menu_list, total_pages

    # GET 요청에 대한 메뉴 목록을 반환합니다.
    def get(self, request):
        user = request.user
        hashtags = request.GET.get('hashtags', None)
        # 현재 사용자가 작성한 모든 메뉴의 store를 가져옵니다.
        user_menus = Menu.objects.filter(store=user)
        user_hashtags = Hashtag.objects.filter(hashtag_author=user)
        user_hashtags = [{'hashtag': tag.hashtag} for tag in user_hashtags]
        # 현재 사용자가 작성한 메뉴 중 해시태그가 포함되거나 전체인 메뉴를 필터링합니다.
        if hashtags and hashtags != "없음":
            # 해당 해시태그를 포함하는 메뉴를 필터링합니다.
            menus = user_menus.filter(hashtags__hashtag=hashtags)
        else:
            menus = user_menus

        # 페이지 번호를 가져옵니다.
        page_number = request.GET.get('page')
        # 페이징된 메뉴 목록과 전체 페이지 수를 가져옵니다.
        menu_list, total_pages = self.get_paginator(menus, page_number)
        return Response(
            {'menus': menu_list, 'page_count': total_pages, "hashtags": hashtags, "user_hashtags": user_hashtags})

    # POST 요청에 대한 새 주문을 생성하고 주문 번호를 반환합니다.
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            # 요청의 본문을 한 번만 읽어서 사용
            user = request.user
            data = request.data
            selected_items = data.get('items', [])
            total_price = data.get('total_price', 0)
            # 오늘 날짜를 가져옵니다.
            today = datetime.now().date()

            # 오늘 생성된 마지막 주문을 가져옵니다.
            last_order = Order.objects.filter(store=user, created_at__date=today).order_by('-id').first()
            if last_order:
                order_number = last_order.order_number + 1
            else:
                order_number = 1

            # 새 주문을 생성합니다.
            new_order = Order.objects.create(
                order_number=order_number,
                order_menu=selected_items,
                total_price=total_price,
                status="A",
                store=user
            )
            return Response({'order_number': new_order.order_number}, status=201)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON'}, status=400)


# 얼굴 인식을 수행하고 추정된 연령에 따라 리디렉션을 수행합니다.
@csrf_exempt
def face_recognition(request):
    if request.method == 'POST' and 'faceImageData' in request.FILES:
        # Get uploaded image
        uploaded_image = request.FILES['faceImageData']
        age_number = face(uploaded_image)

        return JsonResponse({'age_number': age_number})
    return HttpResponse("Please upload an image.")


class orderbot(APIView):
    @staticmethod
    def get(request):
        user = request.user
        recommended_menu = request.GET.get('recommended_menu', '[]')
        print("\n\n params가 string이 붙었을 때:")
        print("\n\n orderbot의 recommended_menu", recommended_menu)
        # JSON 문자열을 파싱하여 리스트로 변환
        recommended_menu = json.loads(recommended_menu)
        print("\n\n recommended_menu 파싱 이후", recommended_menu)
        # 현재 사용자가 작성한 모든 메뉴의 store를 가져옵니다.
        user_menus = Menu.objects.filter(store=user)

        # 추천 메뉴를 미리 정의합니다.
        recommended_list = []
        for recommend in recommended_menu:
            # recommended_list에 메뉴 객체 추가
            menu_items = user_menus.filter(food_name=recommend)
            print("\n\n recommend로 잘 필터해서 가지고 오는지 >>>>", menu_items)
            for menu_item in menu_items:
                recommended_list.append({
                    "food_name": menu_item.food_name,
                    "price": menu_item.price,
                    "img_url": menu_item.img.url
                })
            print("\n\n orderbot의 recommended_list>>>>>>>>>>", recommended_list)
        return Response({'recommends': recommended_list})

    @staticmethod
    def post(request):
        result = 0
        input_text = request.data.get('inputText')
        recommended_menu = request.data.get('recommended_menu')
        print("\n\n input_text>>>> ", input_text)
        print("\n\n recommended_menu>>>> ", recommended_menu)
        current_user = request.user  # POST 요청에서 'input' 값을 가져옴
        types, inputText, recommended_menu = request_type(request, input_text, recommended_menu, current_user)
        print("\n\n category >>>>>> \n\n", types)

        if types == "cart":
            # view_cart로 장바구니 정보를 가져옴
            current_cart = Cart(current_user.username)
            current_cart_get = current_cart.get_cart()
            print("\n\n\n current_cart가 어떤 형태로 들어오는지 : ", current_cart_get)

            result = cart_ai(request, inputText, recommended_menu, current_user, current_cart_get)

            print("\n\n\n result >>>>> ", result) # ('3', '카페라떼,', ['Iced Americano', 'Lemonade', 'Vanilla Latte'])
            username = request.user.username # 나중에 elder_menu에서 연결할 때 다시 구현
            name = result[1] # None 값 # 카드를 누르면 그 카드의 {menu.food_name} 전달이 여기로 되어야 함.
            # json_current_cart = json.loads(current_cart_get) # TypeError: the JSON object must be str, bytes or bytearray, not dict

            if name not in current_cart_get:
                store_id = request.user.id
                menu = Menu.objects.get(store_id = store_id, food_name = name)
                print("\n\n add_to_cart 의 menu 필터링", menu)
                image = menu.img
                price = menu.price
                quantity = result[0]
                item = CartItem(image, name, price, quantity)
                print("CartItem에 들어갔다온 데이터가 잘 받아와지는지 >>>> ", item)
                serializer = CartSerializer(item)
                get_menu = serializer.data
                print("\n\n serializer.data: ", type(serializer.data))
            else:
                print("\n current_cart_get의 타입", type(current_cart_get))
                print("\n current_cart_get 어떻게 생겼나 : ", current_cart_get )
                get_menu = json.loads(current_cart_get[name])
            print("\n\n get_menu 의 타입 : ", type(get_menu))
            get_menu["quantity"] = result[0] # 'str' object does not support item assignment
            print("\n\n quantity의 값이 업데이트 됐는지 : ", get_menu) # {'menu_name': 'Iced Americano', 'quantity': '3', 'price': 5000, 'image': '/media/menu_images/29PM5PMW1I_1_RVIzXq3.jpg'}

            cart = Cart(username)
            print("\n\n\n 메뉴의 수량 확인 : ", get_menu["quantity"])
            if get_menu["quantity"]=='0' or 0:
                print("\n if문 잘 진입했는지:")
                cart.remove(get_menu["menu_name"])
            else:
                cart.add_to_cart(get_menu)

            return Response({"message": "Item added to cart", "cart_items": cart.get_cart()})

            """
            ex ) "바닐라라떼 한 개로 바꿔줘."
            cart_ai를 거쳐서 quantity 값을 받고, action도 받고, 메뉴 이름도 받아와야 함 (음성 인식한 것을 분석하는 함수)
            ex )  바닐라라떼, redis - x = 요청한 quantity, 바꿔줘 == 수량 감소
            --> 여기로 넘겨주면
            redis에 넘길 데이터를 지정해주어야 한다. add_to_cart()
            ex ) 바닐라라떼, 1, 나머지 메뉴 정보
            --> cart.py에서 redis에 그대로 저장해줌. 같은 키값이면 set 으로 덮어씌워준다.
            --> 이 정보가 redis에 저장되어 있으므로 updateCartDisplay()를 해주면 반영 끝.
            """


        elif types == "menu":
            print("\n\n if menu의 input_text>>>> ", input_text)
            print("\n\n if menu의 recommended_menu>>>> ", recommended_menu)
            print("\n\n if menu의 category >>>>>> ", types)
            message, recommended_menu = bot(input_text, current_user)
            return Response({'responseText': message, 'recommended_menu': recommended_menu})
        elif types =="pay":
            print("\n\n elif pay 들어왔는지 \n\n")
            result = 1

        return Response({'result': result})


# 장바구니 페이지 뷰
@api_view(['GET'])
def view_cart(request):
    print("\n\n request 객체라도 나오는지: ", request)
    print("\n\n request의 data: ", request.data)
    username = request.user.username
    print("\n\n\n username 이 잘 들어왔는지: ", username)
    cart = Cart(username)
    context = {"cart_items": cart.get_cart()}
    """
    context >>>>>> 
    {'cart_items': 
    {'Vanilla Latte': '{"menu_name": "Vanilla Latte", "quantity": 2, "price": 5000, "image": "/media/menu_images/348719d11ab5b_j8HnmzP.png"}', 
    '카페라떼': '{"menu_name": "\\uce74\\ud398\\ub77c\\ub5bc", "quantity": 4, "price": 4500, "image": "/media/menu_images/unnamed_iSy0wsw.png"}', 
    'Iced Americano': '{"menu_name": "Iced Americano", "quantity": 2, "price": 5000, "image": "/media/menu_images/29PM5PMW1I_1_RVIzXq3.jpg"}'}}
    """
    print("\n\n\n context가 받아와지는지: ", context)
    cart_data = context.get("cart_items",{})
    print("\n\n cart_data 어떻게 생겼는지 >>>> ", cart_data)
    return Response({"cart_items": context.get("cart_items", {})})


# 장바구니 항목 추가 뷰
@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        username = request.user.username # 나중에 elder_menu에서 연결할 때 다시 구현
        data = json.loads(request.body)
        print("\n\n data >>>>", data)
        print("\n\n request user >>>> ", request.user)
        menu_name = data["menu_name"] # None 값 # 카드를 누르면 그 카드의 {menu.food_name} 전달이 여기로 되어야 함.
        print("\n\n name: " , menu_name)

        cart = Cart(username)
        store_id = request.user.id
        menu = Menu.objects.get(store_id = store_id, food_name = menu_name)
        print("\n\n add_to_cart 의 menu 필터링", menu)
        image = menu.img
        price = menu.price
        quantity = data["quantity"]
        item = CartItem(image, menu_name, price, quantity)
        print("CartItem에 들어갔다온 데이터가 잘 받아와지는지 >>>> ", item)
        serializer = CartSerializer(item)
        print("\n\n serializer.data: ", type(serializer.data))
        cart.add_to_cart(serializer.data)

        return JsonResponse({"message": "Item added to cart", "cart_items": cart.get_cart()})


# 장바구니 항목 수량 수정
@csrf_exempt
@api_view(['POST'])
def add_quantity(request):
    if request.method == "POST":
        username = request.user.username # 나중에 elder_menu에서 연결할 때 다시 구현
        print("\n\n request.user.username: ", username)
        print("\n\n add_quantity username: ", username)
        name = request.POST.get("name") # 카페라떼
        print("\n\n name은 잘 들어왔는지: ", name)
        quantity = int(request.POST.get("quantity")) # 8
        print("\n\n quantity 잘 들어왔는지: ", quantity)

    cart = Cart(username)
    menu = Menu.objects.get(store_id = 2, food_name = name)
    print("\n\n get으로 id, food_name 같이: ", menu)
    # filter_menu = Menu.objects.filter(store_id = 2, food_name = name).first()
    # print("\n\n filter로 id, food_name 같이: ", filter_menu)
    print("\n\n menu가 이렇게 가져오는 게 맞나: ", menu.food_name, menu.img, menu.price)
    image = menu.img
    price = menu.price
    item = CartItem(image, name, price, quantity)
    serializer = CartSerializer(item)
    item_data = serializer.data
    cart.update_quantity(item_data)
    return Response({"message": "장바구니 수량 수정"})


# 장바구니 항목 제거 뷰
@csrf_exempt
@api_view(['POST'])
def remove_from_cart(request, menu_name):
    print("\n\n remove_from_cart() 타는지>>>" )
    username = request.user.username
    print("\n\n remove() username: ", username)
    print("\n\n menu_name: ", menu_name)
    cart = Cart(username)
    cart.remove(menu_name)
    return Response({"message": "해당 메뉴 삭제"})


# 장바구니 전체 삭제 뷰
@csrf_exempt
@api_view(['POST'])
def clear_cart(request):
    username = request.user.username
    cart = Cart(username)
    cart.clear()
    return Response({"message": "장바구니 전체 삭제"})


@csrf_exempt
@api_view(["POST"])
def submit_order(request):
    if request.method == "POST":
        username = request.user.username
        user = request.user
        json_data = request.data
        print("\n\n json_data보기 : ", json_data)
        items = json_data.get('items')
        total = json_data.get('total')
        print("\n\n items : ", items)
        print("\n\n total : ", total)

    # Process the order (database operations, etc.)
    cart = Cart(username)
    # 데이터베이스에 저장

    today = datetime.now().date()

    # 오늘 생성된 마지막 주문을 가져옵니다.
    last_order = Order.objects.filter(store=user, created_at__date=today).order_by('-id').first()
    if last_order:
        order_number = last_order.order_number + 1
    else:
        order_number = 1

    # 새 주문을 생성합니다.
    new_order = Order.objects.create(
        order_number=order_number,
        order_menu=items,
        total_price=total,
        status="A",
        store=user,
    )

    cart.clear()

    return Response({'order_number': new_order.order_number}, status=201)


# redis 실행 확인
def check_redis_connection(request):
    try:
        redis_test(request)
        return JsonResponse({"message": "Redis connected successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def orders_dashboard_data(request):
    orders = Order.objects.all().values()
    df = pd.DataFrame(list(orders))

    if df.empty:
        return JsonResponse({'error': 'No data available'})

    # 날짜별로 분석할 수 있도록 'created_at' 필드를 날짜로 변환
    df['created_at'] = pd.to_datetime(df['created_at']).dt.date

    # 날짜별 주문 수
    daily_orders = df.groupby('created_at').size().reset_index(name='order_count')

    # 날짜별 총 매출
    daily_revenue = df.groupby('created_at')['total_price'].sum().reset_index()

    # 많이 주문된 메뉴
    all_menus = df['order_menu'].apply(pd.Series).stack().reset_index(drop=True).value_counts().reset_index()
    all_menus.columns = ['menu_item', 'count']

    # JSON 응답 생성
    data = {
        'daily_orders': daily_orders.to_dict(orient='records'),
        'daily_revenue': daily_revenue.to_dict(orient='records'),
        'top_menus': all_menus.to_dict(orient='records'),
    }
    return JsonResponse(data)


def orders_dashboard_view(request):
    return render(request, 'admin/orders_dashboard.html')

# def navigation(request):
#     context = {'staff': request.user}
#     print("\n\n\n\n navigation context 어떻게 생겼나>>>>>>>>>>>", context)
#     return render(request, 'includes/navigation.html', context)