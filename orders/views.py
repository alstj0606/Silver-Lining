from .AIbot import AI
import time

import speech_recognition as sr
from rest_framework.views import APIView



class AIbot(APIView):
    def post(self, request):
        r = sr.Recognizer()
        m = sr.Microphone()

        AI.speak("무엇을 도와드릴까요?")
        stop_listening = r.listen_in_background(m, AI.listen)  # 처음 인자는 입력 신호, 두번 째 인자는 실행을 하는 함수

        while True:
            time.sleep(0.1)
