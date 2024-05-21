from rest_framework.views import APIView
from django.shortcuts import render
from .bot import bot
from django.http import JsonResponse
import json

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
