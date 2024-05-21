from openai import OpenAI
from django.conf import settings


def bot(input_text):
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
    return customer_message, selected_choice
