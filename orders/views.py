from rest_framework.views import APIView
from django.shortcuts import render
from .bot import bot
import json
import cv2
from openai import OpenAI
from SilverLining.config import OPEN_API_KEY
import base64
import requests
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from menus.models import Menu
import os
import re


def kiosk_view(request):
    # kiosk.html 템플릿을 렌더링하여 사용자에게 보여줌
    return render(request, 'orders/kiosk.html')



def menu_view(request):
    menus = Menu.objects.all()
    context = {
        'menus': menus
    }
    return render(request, 'orders/menu.html', context)


class AIbot(APIView):
    def post(self, request):
        input_text = request.data.get('inputText')
        current_user = request.user  # POST 요청에서 'input' 값을 가져옴
        message, hashtags = bot(input_text, current_user)
        print(message)
        print(hashtags)
        return JsonResponse({'responseText': message, 'hashtags': hashtags})


@csrf_exempt
def submit_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_items = data.get('items', [])
        total_price = data.get('total_price', 0)

        # 현재 날짜
        today = datetime.now().date()

        # 마지막 주문이 오늘이면 1추가 아니면 1번 부터 시작
        last_order = Order.objects.filter(created_at__date=today).order_by('-id').first()
        if last_order:
            order_number = last_order.order_number + 1
        else:
            order_number = 1

        # 새로운 데이터 저장
        new_order = Order.objects.create(
            order_number=order_number,
            order_menu=selected_items,
            total_price=total_price,
            status="A"
        )

        # order_number json으로 반환
        return JsonResponse({'order_number': new_order.order_number}, status=201)


def order_complete(request, order_number):
    context = {
        'order_number': order_number,
    }
    return render(request, 'orders/order_complete.html', context)


def get_menus(request):
    hashtags = request.GET.get('hashtags', None)
    print("음성인식 >>>>", hashtags)
    if hashtags:
        menus = Menu.objects.filter(hashtags__hashtag=hashtags)
    else:
        menus = Menu.objects.all()
    menu_list = [
        {
            'food_name': menu.food_name,
            'price': menu.price,
            'img_url': menu.img.url if menu.img else ''
        } for menu in menus
    ]
    return JsonResponse({'menus': menu_list})


def order_complete(request, order_number):
    context = {
        'order_number': order_number,
    }
    return render(request, 'orders/order_complete.html', context)

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
        print("ret>>>>>>>>>>>", ret)
        print("frame>>>>>>>>>", frame)


        if not ret:
            raise Exception("Cannot read frame from webcam")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if faces.any():
            print("faces>>>>>>>", faces)
            break

    cap.release()

    image_path = "face.jpg"
    print("image_path>>>>>>>>>>", image_path)
    cv2.imwrite(image_path, frame)


    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        print("encoded_image>>>>>>>>>>>", encoded_image)
    # base64_image = encoded_image(image_path)
    base64_image = f"data:image/jpeg;base64,{encoded_image}"

    print("base64_image>>>>>>>>>", base64_image)

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
            "text": "Although age can be difficult to predict, please provide an approximate number for how old the person in the photo appears to be. Please consider that Asians tend to look younger than you might think.And Please provide an approximate age in 10-year intervals such as teens, 20s, 30s, 40s, 50s, 60s, 70s, or 80s. Please return the inferred age in the format 'Estimated Age: [inferred age]'."
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
    print("api통과??>>>>>>>>>>>>")
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
        return render(request, 'orders/menu_big.html')
    
    return render(request, 'orders/menu.html')

