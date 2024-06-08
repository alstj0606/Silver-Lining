import base64
import json
import os
from datetime import datetime

import cv2
import numpy as np
import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView

from SilverLining.config import OPEN_API_KEY  # SilverLining 앱의 설정에서 OPEN_API_KEY를 가져옵니다.
from menus.models import Menu, Hashtag  # Menu와 Hashtag 모델을 가져옵니다.
from .bot import bot  # AI 봇 기능을 처리하는 함수를 가져옵니다.
from .models import Order  # 주문 모델을 가져옵니다.
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # 페이지네이션을 위한 라이브러리들을 가져옵니다.
from django.utils.decorators import method_decorator  # 데코레이터를 사용하기 위한 라이브러리를 가져옵니다.
from django.conf import settings  # Django 설정을 가져옵니다.
from django.utils import translation  # Django의 다국어 지원을 위한 translation 모듈을 가져옵니다.
from django.http import JsonResponse

from .orderbot import request_type, cart_ai
from .cart import CartItem, Cart, redis_test
from .serializers import CartSerializer

from rest_framework.decorators import api_view


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

        # Read the image using OpenCV
        image_data = uploaded_image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 얼굴 인식을 위한 분류기를 로드합니다.
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # 흑백 이미지로 변환합니다.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 얼굴을 감지합니다.
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            # 이미지를 저장하고 base64로 변환합니다.
            image_path = "face.jpg"
            cv2.imwrite(image_path, frame)

            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

            base64_image = f"data:image/jpeg;base64,{encoded_image}"

            # OpenAI API에 요청합니다.
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPEN_API_KEY}"
            }

            instruction = """
                                Although age can be difficult to predict, please provide an approximate number for how old the person in the photo appears to be. 
                                Please consider that Asians tend to look younger than you might think.
                                And Please provide an approximate age in 10-year intervals such as teens, 20s, 30s, 40s, 50s, 60s, 70s, or 80s.
                                When you return the value, remove the 's' in the end of the age interval.
                                For example, when you find the person to be in their 20s, just return the value as 20.
                                Please return the inferred age in the format 'Estimated Age: [inferred age]'.
                                """

            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": instruction,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": base64_image
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300
            }
            # OpenAI API로 요청을 보냅니다.
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            try:
                os.remove(image_path)
                print(f"{image_path} 이미지가 삭제되었습니다.")

            except FileNotFoundError:
                print(f"{image_path} 이미지를 찾을 수 없습니다.")

            # OpenAI API에서 반환된 응답을 파싱합니다.
            ai_answer = response.json()
            print("ai_answer", ai_answer)
            # 추정된 나이를 가져옵니다.
            age_message = ai_answer["choices"][0]['message']['content']
            age = age_message.split("Estimated Age: ")[1].strip()
            age_number = int(age)
            print("당신의 얼굴나이 : ", age_number)

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
            username = request.user.username 
            name = result[1]
            # json_current_cart = json.loads(current_cart_get) # TypeError: the JSON object must be str, bytes or bytearray, not dict
            
            if name not in current_cart_get:
                store_id = request.user.id
                menu = Menu.objects.get(store_id = store_id, food_name = name)
                print("\n\n update_cart_menu 의 menu 필터링", menu)
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
            if get_menu["quantity"] == '0' or 0:
                cart.remove(get_menu["menu_name"])
                print("\n\n cart.remove 잘 되고 있는지 >>>>>>>>>", get_menu)
            else:
                cart.add_to_cart(get_menu)

            return Response({"message": "Item added to cart", "cart_items": cart.get_cart()})


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
def update_cart_menu(request):
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
        print("\n\n update_cart_menu 의 menu 필터링", menu)
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
    print("\n\n cart>>>>>>>>>", cart)
    res = cart.clear()
    print("\n\n cart.clear 잘 가는지>>>>>>>>>", res)
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
