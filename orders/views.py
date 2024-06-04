import base64
import json
import os
from datetime import datetime

import cv2
import requests
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
            menu_items = user_menus.filter(food_name=recommend)
            for menu_item in menu_items:
                recommended_list.append({
                    "food_name": menu_item.food_name,
                    "price": menu_item.price,
                    "img_url": menu_item.img.url
                })
        return Response({'recommends': recommended_list})

    @staticmethod
    def post(request):
        # POST 요청을 처리하는 메소드입니다.
        # AI 봇에게 입력된 텍스트를 전달하고 응답을 받습니다.
        input_text = request.data.get('inputText')
        current_user = request.user
        message, recommended_menu = bot(request, input_text, current_user)
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
def face_recognition(request):
    # 웹캠 열기
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise Exception("Cannot open Webcam")

    # 얼굴 인식을 위한 분류기를 로드합니다.
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # 프레임 읽기
    while True:
        ret, frame = cap.read()

        if not ret:
            raise Exception("Cannot read frame from webcam")
        # 흑백 이미지로 변환합니다.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 얼굴을 감지합니다.
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            break

    # 웹캠을 닫습니다.
    cap.release()

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

    # 추정된 나이를 가져옵니다.
    age_message = ai_answer["choices"][0]['message']['content']
    age = age_message.split("Estimated Age: ")[1].strip()
    age_number = int(age)
    print("당신의 얼굴나이 : ", age_number)

    if age_number >= 60:
        return redirect("orders:elder_start")

    return redirect("orders:menu")

class elderMenuAPI(APIView):
    def get():
        pass

    def post():
        pass


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
            result = cart_ai(request, inputText, recommended_menu, current_user)
            ## js로 넘어가서 해당 메뉴를 몇 번 클릭해서 더하거나 몇 개 빼주거나
            #### category: cart, inputText: 아메리카노 두 잔 넣어줘 
            #### gpt 가 받아서 어떤 메뉴를 , 몇 개를, 어
            ## 1. orderbot.py에서 저장된 텍스트에서 맥락을 파악해 넘겨주는 함수가 필요함 (어떤 메뉴를/ 몇개를/ 어떻게) + 어떤 메뉴의 정확도 향상을 위해서는 recommended menu도 필요 (왼쪽 거, 처음 거 등)
            ## 2. axios.get으로 여기서 넘겨준 결과를 가지고 장바구니 관련 기능을 실행해주어야 함. "아메리카노/두개/장바구니에 추가", "바닐라라떼/하나/장바구니에서 삭제"
            ## 예로 Response({'menu_name':menu_name, 'number':number, 'action': action})
            ## menu_name은 현재 우리가 가지고 있는 메뉴 내에서만 파악하라고 해야 함
            ## 숫자 파악에서 그냥 "바닐라라떼 줘" 에도 숫자를 파악할 수 있도록 해야 함. 0개로 출력되지 않게.
            ## action은 add, delete 등의 옵션 / 수정도 add, delete로 구현할 수 있을지도? ( ~ 넣고 ~빼줘, ~를 ~로 바꿔줘)
            
        elif types == "menu":
            print("\n\n if menu의 input_text>>>> ", input_text)
            print("\n\n if menu의 recommended_menu>>>> ", recommended_menu)
            print("\n\n if menu의 category >>>>>> ", types)
            message, recommended_menu = bot(request, input_text, current_user)
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
    # {"username": "mega"}
    username = request.user.username
    print("\n\n\n username 이 잘 들어왔는지: ", username)
    cart = Cart(username)
    context = {"cart_items": cart.get_cart()}
    print("\n\n\n context가 받아와지는지: ", context)
    return Response({"context": context})

# 장바구니 항목 추가 뷰
@csrf_exempt
def add_to_cart(request): # 무조건 하나를 더한다
    if request.method == "POST":
        username = request.user.username # 나중에 elder_menu에서 연결할 때 다시 구현
        data = json.loads(request.body)
        print("\n\n data >>>>", data)
        print("\n\n request user >>>> ", request.user)
        name = data["menu_name"] # None 값 # 카드를 누르면 그 카드의 {menu.food_name} 전달이 여기로 되어야 함.
        print("\n\n name: " , name)
        
        cart = Cart(username)
        store_id = request.user.id
        menu = Menu.objects.get(store_id = store_id, food_name = name)
        print("\n\n add_to_cart 의 menu 필터링", menu)
        image = menu.img
        price = menu.price
        quantity = data["quantity"]
        item = CartItem(image, name, price, quantity)
        print("CartItem에 들어갔다온 데이터가 잘 받아와지는지 >>>> ", item)
        serializer = CartSerializer(item)
        print("\n\n serializer.data: ", type(serializer.data))
        cart.add_to_cart(serializer.data)
        
        return JsonResponse({"message": "Item added to cart"})

    
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
@api_view(['POST'])
def submit_order(request):
    # Handle order submission logic
    username = request.user.username
    items = request.data.get("items")
    total = request.data.get("total")

    # Process the order (database operations, etc.)
    cart = Cart(username)
    cart.clear()
    return Response({"message": "Order submitted successfully"})

# redis 실행 확인
def check_redis_connection(request):
    try:
        redis_test(request)
        return JsonResponse({"message": "Redis connected successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# 1. html 장바구니와 연결
# 4. 장바구니의 데이터 결제하기 누르면 order에 전달되도록 (지금 [] 전달 되고 있음)


# 2. 음성으로 뽑아낸 것 전달 -> views.py 에서 실행 하는 것
# 3. drf API로... ?? 후순위 (현재 작동이 잘 되고 있음)
# 5. 음성 대기 - speak() & startSpeechRecognition() 무한 반복 while 사용하면 될 듯
