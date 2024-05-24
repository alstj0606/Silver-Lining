import base64
import json
import os
import re
from datetime import datetime

import cv2
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from SilverLining.config import OPEN_API_KEY
from menus.models import Menu
from .bot import bot
from .models import Order

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator


def menu_view(request):
    return render(request, 'orders/menu.html')


def menu_view_big(request):
    return render(request, 'orders/menu_big.html')


class AIbot(APIView):
    @staticmethod
    def post(request):
        input_text = request.data.get('inputText')
        current_user = request.user  # POST 요청에서 'input' 값을 가져옴
        message, hashtags = bot(input_text, current_user)
        print(message)
        print(hashtags)
        return JsonResponse({'responseText': message, 'hashtags': hashtags})


def order_complete(request, order_number):
    context = {
        'order_number': order_number,
    }
    return render(request, 'orders/order_complete.html', context)


class MenusAPI(APIView):

    @staticmethod
    def get_paginator(menus, page_number):
        paginator = Paginator(menus, 6)  # 페이지 당 6개의 메뉴

        try:
            menus = paginator.page(page_number)
        except PageNotAnInteger:
            menus = paginator.page(1)
        except EmptyPage:
            menus = paginator.page(paginator.num_pages)

        menu_list = [
            {
                'food_name': menu.food_name,
                'price': menu.price,
                'img_url': menu.img.url if menu.img else ''
            } for menu in menus
        ]

        total_pages = paginator.num_pages

        return menu_list, total_pages

    def get(self, request):
        user = request.user
        hashtags = request.GET.get('hashtags', None)
        if hashtags:
            menus = Menu.objects.filter(hashtags__hashtag=hashtags)
        else:
            menus = Menu.objects.all()

        page_number = request.GET.get('page')
        menu_list, total_pages = self.get_paginator(menus, page_number)
        return JsonResponse({'menus': menu_list, 'page_count': total_pages})

    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            # 요청의 본문을 한 번만 읽어서 사용
            data = json.loads(request.body)
            selected_items = data.get('items', [])
            total_price = data.get('total_price', 0)

            today = datetime.now().date()

            last_order = Order.objects.filter(created_at__date=today).order_by('-id').first()
            if last_order:
                order_number = last_order.order_number + 1
            else:
                order_number = 1

            new_order = Order.objects.create(
                order_number=order_number,
                order_menu=selected_items,
                total_price=total_price,
                status="A"
            )

            return JsonResponse({'order_number': new_order.order_number}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


def start_order(request):
    return render(request, 'orders/start_order.html')


def face_recognition(request):
    # 웹캠 열기
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise Exception("Cannot open Webcam")

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # 프레임 읽기
    while True:
        ret, frame = cap.read()
        # print("ret>>>>>>>>>>>", ret)
        # print("frame>>>>>>>>>", frame)

        if not ret:
            raise Exception("Cannot read frame from webcam")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            print("faces>>>>>>>", faces)
            break

    cap.release()

    image_path = "face.jpg"
    # print("image_path>>>>>>>>>>", image_path)
    cv2.imwrite(image_path, frame)

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        # print("encoded_image>>>>>>>>>>>", encoded_image)
    # base64_image = encoded_image(image_path)
    base64_image = f"data:image/jpeg;base64,{encoded_image}"

    # print("base64_image>>>>>>>>>", base64_image)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPEN_API_KEY}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """ Although age can be difficult to predict, 
                        please provide an approximate number for how old the person in the photo appears to be.
                         Please consider that Asians tend to look younger than you might think.
                         And Please provide an approximate age in 10-year intervals such as teens,
                          20s, 30s, 40s, 50s, 60s, 70s, or 80s. 
                          Please return the inferred age in the format 'Estimated Age: [inferred age]'.
                          """
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
    # print("api통과??>>>>>>>>>>>>")
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    try:
        os.remove(image_path)
        print(f"{image_path} 이미지가 삭제되었습니다.")

    except FileNotFoundError:
        print(f"{image_path} 이미지를 찾을 수 없습니다.")

    ai_answer = response.json()

    age_message = ai_answer["choices"][0]['message']['content']

    age = age_message.split("Estimated Age: ")[1].strip()
    number = re.findall(r'\d+', age)
    age_number = int(number[0])

    if age_number >= 60:
        return redirect("orders:menu_big")

    return redirect("orders:menu")
