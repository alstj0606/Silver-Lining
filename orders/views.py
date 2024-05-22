from rest_framework.views import APIView
from django.shortcuts import render
from .bot import bot
import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from menus.models import Menu
from django.contrib.sessions.models import Session


def menu_view(request):
    hashtags = request.session.get('hashtags', None)
    if hashtags:
        menus = Menu.objects.filter(hashtags__hashtag=hashtags)
    else:
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
        request.session['hashtags'] = hashtags
        return JsonResponse({'responseText': message})


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
    # 이전 세션 정보 삭제
    if 'hashtags' in request.session:
        del request.session['hashtags']

    context = {
        'order_number': order_number,
    }
    return render(request, 'orders/order_complete.html', context)
