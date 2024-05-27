from openai import OpenAI
from django.conf import settings
from menus.models import Menu, Hashtag


def get_user_menu_and_hashtags(user):
    # 현재 로그인된 사용자의 메뉴 가져오기
    user_menu = Menu.objects.filter(store=user)
    # 메뉴에 연결된 해시태그 가져오기
    user_hashtags = Hashtag.objects.filter(menu_items__in=user_menu).distinct()

    # 메뉴 이름과 해시태그 문자열로 변환
    menu_list = [menu.food_name for menu in user_menu]
    hashtag_list = [hashtag.hashtag for hashtag in user_hashtags]

    return menu_list, hashtag_list


def bot(request, input_text, current_user):
    client = OpenAI(api_key=settings.OPEN_API_KEY)

    # 사용자의 카테고리 가져오기
    category = current_user.category

    # 사용자의 메뉴 및 해시태그 가져오기
    menu, hashtags = get_user_menu_and_hashtags(current_user)

    # 카테고리에 따라 시스템 지침 작성
    if category == "CH":
        category_text = "치킨"
    elif category == "CA":
        category_text = "카페"
    else:
        category_text = "음식점"

    system_instructions = f"""
    이제부터 너는 "{category_text} 직원"이야. 너는 고객의 말에 따라 메뉴를 추천해 줘야해. 우리 가게에는 {menu}가 있어. 
    그리고 아래의 카테고리 중에서 고객의 질문과 관련이 있는 항목을 선택해줘: {hashtags}. 
    선택된 항목은 '선택된 항목: [항목]' 형식으로 반환해줘. 
    만약에 해당하는 선택항목이 없다면 '선택된 항목: 없음'이라고 반환해줘.
    그리고 고객에게 전달할 메시지를 작성해줘. 한 문장으로 서비스를 하는 직원처럼 '메세지: [내용]'으로 작성해줘.
    마지막으로, 추천하는 메뉴의 이름을 '추천 메뉴: [메뉴 이름]' 형식으로 작성해줘. 반드시 추천하는 메뉴는 한가지만 추천해줘.
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": input_text},
        ],
    )

    ai_response = completion.choices[0].message.content
    selected_choice = None
    customer_message = ""
    recommended_menu = ""

    try:
        for line in ai_response.split('\n'):
            if line.startswith('선택된 항목:'):
                selected_choice = line.split('선택된 항목: ')[1].strip()
            elif line.startswith('메세지:'):
                customer_message = line.split('메세지: ')[1].strip()
            elif line.startswith('추천 메뉴:'):
                recommended_menu = line.split('추천 메뉴: ')[1].strip()

    except IndexError:
        selected_choice = "선택된 항목: 없음"
        customer_message = "죄송합니다. 다시 한 번 이야기 해주세요"
        recommended_menu = ""

    # 선택된 항목이 있으면 출력
    if selected_choice != "선택된 항목: 없음":
        print(f"선택된 항목: {selected_choice}")

    else:
        print("관련 항목을 찾지 못했습니다.")

    customer_message = customer_message.strip()
    return customer_message, selected_choice, recommended_menu

