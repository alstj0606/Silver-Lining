from rest_framework.views import APIView
from django.shortcuts import render
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
