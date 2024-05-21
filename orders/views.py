from rest_framework.views import APIView
from django.shortcuts import render, redirect
from .bot import bot
from django.http import JsonResponse


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
        # 주문을 제출하는 POST 요청을 처리합니다.
        # 요청에서 데이터를 추출합니다.
        # 주문을 데이터베이스에 저장합니다.
        # 예시를 위해, 'name'과 'price'를 POST 데이터에서 가져오는 것으로 가정합니다.
        name = request.POST.get('name')
        price = request.POST.get('price')
        # 주문 객체를 생성하거나 가져옵니다.
        # order, created = Order.objects.get_or_create(name=name, defaults={'price': price})
        order_number = 100
        # 주문 완료 페이지로 주문 번호와 함께 리다이렉트합니다.
        return redirect('order_complete', order_number=order_number)


def order_complete(request, order_number):
    context = {
        'order_number': order_number,
    }
    return render(request, 'orders/order_complete.html', context)
