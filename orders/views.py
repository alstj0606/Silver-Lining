import base64
import json
import os
from datetime import datetime

import cv2
import requests
from django.http import JsonResponse
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
from .orderbot import request_type


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
def face_recognition(request):
    # 이미지 데이터 확인
    if 'faceImageData' in request.FILES:
        # 이미지 파일을 받아옴
        base64_image = request.FILES['faceImageData']
        # 이미지 파일 처리 로직 추가
        # 예) 이미지 저장, 처리 등
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
    else:
        # 이미지가 없음 에러 응답
        response_data = {'error': 'No image file received'}
        return JsonResponse(response_data, status=400)



class elderMenuAPI(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass


class orderbot(APIView):
    @staticmethod
    def get(request):
        user = request.user
        recommended_menu = request.GET.get('recommended_menu', '[]')

        # JSON 문자열을 파싱하여 리스트로 변환
        recommended_menu = json.loads(recommended_menu)
        # 현재 사용자가 작성한 모든 메뉴의 store를 가져옵니다.
        user_menus = Menu.objects.filter(store=user)

        # 추천 메뉴를 미리 정의합니다.
        recommended_list = []
        for recommend in recommended_menu:
            # recommended_list에 메뉴 객체 추가
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
        result = 0
        input_text = request.data.get('inputText')
        current_user = request.user  # POST 요청에서 'input' 값을 가져옴
        category, inputText = request_type(request, input_text, current_user)
        print("\n\n category >>>>>> \n\n", category)
        if category == "cart":
            result = cart(inputText)
            ## orderbot.py 가서 맥락 파악 필요 (메뉴, 개수, 행동) / 정확도를 위해서 recommended_menu 도 필요
            ## js로 넘어가서 해당 메뉴를 몇 번 클릭해서 더하거나 몇 개 빼주거나
        elif category == "menu":
            result = 2
            ## orderbot.py 안 가도 됨
            ## js로 넘어가서 음성 재인식 버튼 눌러주는 거 (speechRecognition() ~~~ 해서 메뉴추천)
        elif category == "pay":
            print("\n\n elif pay 들어왔는지 \n\n")
            result = 1
            ## 결제해줘, 라고 했는데 (장바구니가 비어있으면 안 됨) --> js 에서
            ## orderbot.py 안 가도 됨
            ## js로 넘어가서 결제하기 버튼 눌러주기
        return Response({'result': result})


def cart(inputText):
    pass

# def sending_post(axios.post):
#     data = request.data
#     if type == menu:
#         bot()
#     elif type == cart:
#         function()
#     else type == pay:
#         pay()
