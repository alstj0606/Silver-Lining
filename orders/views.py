from .AIbot import AI
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import render


def kiosk_view(request):
    # kiosk.html 템플릿을 렌더링하여 사용자에게 보여줌
    return render(request, 'kiosk.html')


class AIbot(APIView):
    def post(self, request):
        ai_instance = AI()
        input_btn = request.data.get('input')  # POST 요청에서 'input' 값을 가져옴
        print(input_btn)
        if input_btn == 'on':
            ai_instance.input()  # 마이크 ON일 경우에만 입력 시작
        elif input_btn == 'off':
            ai_instance.stop_microphone()  # 마이크 OFF일 경우 마이크 중지
        return Response({"message": "AI 답변이 완료되었습니다."}, status=status.HTTP_200_OK)

