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

from .orderbot import request_type, cart_ai # 음성 AI 처리 관련 함수
from .cart import CartItem, Cart # 장바구니 redis 저장 관련
from .serializers import CartSerializer # 장바구니 직렬화 관련

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


# 고령층 템플릿 
def elder_start(request):
    return render(request, "orders/elder_start.html")

# 고령층 템플릿
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


# 고령층의 AI 관련 요청을 처리합니다.
class orderbot(APIView):
    # AI의 추천메뉴를 조회합니다.
    @staticmethod
    def get(request):
        user = request.user
        recommended_menu = request.GET.get('recommended_menu', '[]')
        # JSON 문자열을 파싱하여 리스트로 변환
        recommended_menu = json.loads(recommended_menu)
        # 현재 사용자가 작성한 모든 메뉴를 가져옵니다.
        user_menus = Menu.objects.filter(store=user)
        recommended_list = []
        for recommend in recommended_menu:
            # 추천 메뉴를 현재 사용자의 메뉴에서 필터링합니다.
            menu_items = user_menus.filter(food_name=recommend)
            for menu_item in menu_items:
                recommended_list.append({
                    "food_name": menu_item.food_name,
                    "price": menu_item.price,
                    "img_url": menu_item.img.url
                })
        return Response({'recommends': recommended_list})
    
    # POST 요청으로 음성 재입력이 들어왔을 때
    @staticmethod
    def post(request):
        result = 0
        input_text = request.data.get('inputText')
        recommended_menu = request.data.get('recommended_menu')
        current_user = request.user
        # AI에 음성 transcript, 기존 추천 받았던 메뉴, 현재 점주 정보를 전달합니다.
        types, inputText, recommended_menu = request_type(request, input_text, recommended_menu, current_user)
        # AI가 장바구니 관련 음성 입력이라고 판단했을 경우
        if types == "cart":
            # 현재 장바구니를 확인합니다.
            current_cart = Cart(current_user.username)
            current_cart_get = current_cart.get_cart()
            # AI에게 음성 입력, 기존 추천 메뉴, 현재 점주, 현재 장바구니를 전달하여 응답을 받습니다.
            result = cart_ai(request, inputText, recommended_menu, current_user, current_cart_get)
            username = request.user.username
            # 상태를 수정하려는 메뉴의 이름
            name = result[1]
            # 현재 장바구니에 해당 메뉴가 없을 때 메뉴를 데이터베이스에서 불러옵니다.
            if name not in current_cart_get:
                store_id = request.user.id
                menu = Menu.objects.get(store_id = store_id, food_name = name)
                image = menu.img
                price = menu.price
                quantity = result[0]
                item = CartItem(image, name, price, quantity)
                serializer = CartSerializer(item)
                get_menu = serializer.data
            # 해당 메뉴가 있으면 상태를 불러옵니다.
            else:
                get_menu = json.loads(current_cart_get[name])
            # 수정하려는 메뉴의 수량을 가져옵니다.
            get_menu["quantity"] = result[0]
            # redis에서 처리할 수 있도록 넘겨줍니다.
            cart = Cart(username)
            # 수정한 수량이 0일 경우, 장바구니에서 삭제해주고 이외의 경우 수량을 업데이트하여 redis에 저장합니다.
            if get_menu["quantity"]=='0' or 0:
                cart.remove(get_menu["menu_name"])
            else:
                cart.add_to_cart(get_menu)
            return Response({"message": "Item added to cart", "cart_items": cart.get_cart()})
        
        # AI가 새 메뉴를 추천해달라는 요청이라고 판단했을 경우
        elif types == "menu":
            message, recommended_menu = bot(input_text, current_user)
            return Response({'responseText': message, 'recommended_menu': recommended_menu})
        
        # AI가 결제 요청이라고 판단했을 경우
        elif types =="pay":
            result = 1

        return Response({'result': result})

# 장바구니 현재 상태 조회
@api_view(['GET'])
def view_cart(request):
    username = request.user.username
    cart = Cart(username)
    context = {"cart_items": cart.get_cart()}
    cart_data = context.get("cart_items",{})
    return Response({"cart_items": cart_data})

# 장바구니에 항목 추가
@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        username = request.user.username
        data = json.loads(request.body)
        menu_name = data["menu_name"]

        cart = Cart(username)
        store_id = request.user.id
        menu = Menu.objects.get(store_id = store_id, food_name = menu_name)
        image = menu.img
        price = menu.price
        quantity = data["quantity"]
        item = CartItem(image, menu_name, price, quantity)
        serializer = CartSerializer(item)
        cart.add_to_cart(serializer.data)

        return JsonResponse({"message": "Item added to cart", "cart_items": cart.get_cart()})

# 장바구니 항목 수량 수정
@csrf_exempt
@api_view(['POST'])
def add_quantity(request):
    if request.method == "POST":
        username = request.user.username
        name = request.POST.get("name")
        quantity = int(request.POST.get("quantity"))

    cart = Cart(username)
    menu = Menu.objects.get(store_id = 2, food_name = name)
    image = menu.img
    price = menu.price
    item = CartItem(image, name, price, quantity)
    serializer = CartSerializer(item)
    item_data = serializer.data
    cart.update_quantity(item_data)
    return Response({"message": "장바구니 수량 수정"})

# 장바구니 항목 제거
@csrf_exempt
@api_view(['POST'])
def remove_from_cart(request, menu_name):
    username = request.user.username
    cart = Cart(username)
    cart.remove(menu_name)
    return Response({"message": "해당 메뉴 삭제"})

# 장바구니 전체 삭제
@csrf_exempt
@api_view(['POST'])
def clear_cart(request):
    username = request.user.username
    cart = Cart(username)
    cart.clear()
    return Response({"message": "장바구니 전체 삭제"})

# 결제 후 주문번호 출력
@csrf_exempt
@api_view(["POST"])
def submit_order(request):
    if request.method == "POST":
        username = request.user.username
        user = request.user
        json_data = request.data
        items = json_data.get('items')
        total = json_data.get('total')

    # 데이터베이스에 주문 저장
    cart = Cart(username)

    # 오늘 생성된 마지막 주문을 가져옵니다.
    today = datetime.now().date()
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

    # Top 5 메뉴만 가져오기
    top_menus = all_menus.head(5)

    # 데이터를 템플릿으로 전달
    context = {
        'daily_orders': daily_orders.values.tolist(),
        'daily_revenue': daily_revenue.values.tolist(),
        'top_menus': top_menus.to_dict(orient='records')
    }
    
    return render(request, 'path_to_template/orders_dashboard.html', context)

def orders_dashboard_view(request):
    return render(request, 'admin/orders_dashboard.html')

# def navigation(request):
#     context = {'staff': request.user}
#     print("\n\n\n\n navigation context 어떻게 생겼나>>>>>>>>>>>", context)
#     return render(request, 'includes/navigation.html', context)