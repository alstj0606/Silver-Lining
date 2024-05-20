import os
import time
import speech_recognition as sr
from gtts import gTTS
from openai import OpenAI
import pygame
from django.conf import settings


class AI:
    # 음성 인식 (듣기, STT)
    def __init__(self):
        self.stop_listening = None
        self.r = sr.Recognizer()
        self.m = sr.Microphone()

    def stop_microphone(self):
        print(self.stop_listening)
        if self.stop_listening is not None:
            self.stop_listening(wait_for_stop=False)
            self.speak("마이크 입력을 종료 합니다.")

    def listen(self, recognizer, audio):  # 리스너 메서드에 recognizer와 audio 매개변수 추가
        try:
            text = recognizer.recognize_google(audio, language='ko-KR')
            print("[고객] : " + text)
            self.answer(text)
        except sr.UnknownValueError:
            print("인식 실패")
        except sr.RequestError as e:
            print("요청 실패 : {0}".format(e))

    # 대답
    def answer(self, input_text):
        client = OpenAI(api_key=settings.OPEN_API_KEY)
        menu = ["아메리카노", "아이스아메리카노", "카푸치노", "딸기스무디", "블루베리스무디"]  # 데이터 베이스에서 목록조회
        category = ["시원한", "커피", "따뜻한", "과일", "딸기", "블루베리"]
        system_instructions = f"""
            이제부터 너는 "카페 직원"이야. 
            너는 고객의 말에 따라 음료를 추천해 줘야해 우리가게에는 {menu}가 있어.
            그리고 아래의 카테고리 중에서 고객의 질문과 관련이 있는 항목을 선택해줘: {category}
            선택된 항목은 '선택된 항목: [항목]' 형식으로 반환하고,
            고객에게 전달할 메시지는 한 문장으로 서비스를 하는 직원처럼 '메세지: "내용"'으로 작성해줘.
        """
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": input_text},
            ],
        )
        ai_response = completion.choices[0].message.content

        # 선택된 항목과 고객 메시지 추출
        selected_choice = None
        customer_message = ""
        try:
            for line in ai_response.split('\n'):
                if line.startswith('선택된 항목:'):
                    selected_choice = line.split('선택된 항목: ')[1].strip()
                else:
                    customer_message += line.split('메세지: ')[1].strip()
        except IndexError:
            selected_choice = None
            customer_message = "죄송합니다. 다시 한 번 이야기 해주세요"
        # 선택된 항목이 있으면 출력
        if selected_choice:
            print(f"선택된 항목: {selected_choice}")
        else:
            print("관련 항목을 찾지 못했습니다.")

        customer_message = customer_message.strip()
        self.speak(customer_message)

    # 소리내어 읽기 (TTS)
    @staticmethod
    def speak(text):
        print("[AI도우미] : " + text)
        file_name = "voice.mp3"
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except PermissionError:
                print(f"파일 {file_name}이(가) 다른 프로세스에 의해 사용 중입니다.")
                return
        tts = gTTS(text=text, lang='ko')
        tts.save(file_name)
        pygame.mixer.init()
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # 음악이 재생 중인지 확인
            time.sleep(0.1)
        pygame.mixer.quit()
        if os.path.exists(file_name):  # 음성 하고 파일 삭제
            os.remove(file_name)

    def input(self):
        r = sr.Recognizer()
        m = sr.Microphone()

        self.speak("무엇을 도와드릴까요?")
        self.stop_listening = r.listen_in_background(m, self.listen)  # 처음 인자는 입력 신호, 두번 째 인자는 실행을 하는 함수

        print(self.stop_listening)
        while True:
            time.sleep(0.1)
