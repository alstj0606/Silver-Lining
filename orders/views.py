from rest_framework.views import APIView
from django.shortcuts import render
from .bot import bot
from django.http import JsonResponse
import json
import cv2
from openai import OpenAI
from SilverLining.config import OPEN_API_KEY
import base64
import requests

def kiosk_view(request):
    # kiosk.html 템플릿을 렌더링하여 사용자에게 보여줌
    return render(request, 'orders/kiosk.html')


def menu_view(request):
    # kiosk.html 템플릿을 렌더링하여 사용자에게 보여줌
    return render(request, 'orders/menu.html')


class AIbot(APIView):
    def post(self, request):
        input_text = request.data.get('inputText')  # POST 요청에서 'input' 값을 가져옴
        message, category = bot(input_text)
        print(message)
        print(category)
        return JsonResponse({'responseText': message})


def submit_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_items = data.get('items', [])
        total_price = data.get('total_price', 0)

        print(selected_items)
        print(total_price)

        # 여기서 선택된 상품들과 총 금액을 이용하여 주문을 처리하고, 주문 번호를 생성합니다.
        order_number = 404

        return JsonResponse({'order_number': order_number})


def order_complete(request, order_number):
    context = {
        'order_number': order_number,
    }
    return render(request, 'orders/order_complete.html', context)


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

    print("response.json()>>>>>>>>>>", response.json())
    return JsonResponse(response.json())

    