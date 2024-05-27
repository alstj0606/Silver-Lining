import re

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
    print(input_text)
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

    system_data = f"""
        You are considered a staff member related to {category_text}.
        Our store offers the following menu items: {menu}.
        Additionally, we use the following hashtags in our store: {hashtags}.
        """

    system_output = f"""
        The format of the data I desire as a result is:
        "Message: [content]
        Recommended Menu: [menu_name]"
        For the "Recommended Menu" section, select three options that are most closely related to the customer's request and rank them accordingly. 
        For example, if there's only one recommended menu, it should be formatted as "Recommended Menu: menu_name". 
        If there are two recommended menus, it should be "Recommended Menu: menu_name, menu_name", 
        and if there are three recommended menus, it should be "Recommended Menu: menu_name, menu_name, menu_name", listing them in order of priority.
        """

    system_instructions = f"""
        When delivering a message to the customer, 
        kindly determine their desired menu item and keep the message concise, preferably to one sentence. 
        The recommended menu item must be chosen from the list of {menu}.
        """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_data},
            {"role": "system", "content": system_output},
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": input_text},
        ],
    )

    ai_response = completion.choices[0].message.content
    print(ai_response)
    customer_message = ""
    recommended_menu = []

    try:
        for line in ai_response.split('\n'):
            line = line.strip()  # Remove whitespace from both ends
            # line = re.sub(r'[\[\]\'\"]', '', line)  # Remove square brackets
            if line.startswith('Message:'):
                customer_message = line.split('Message: ')[1].strip()
            elif line.startswith('Recommended Menu:'):
                recommended_menu = line.split('Recommended Menu: ')[1].strip().split(', ')

    except IndexError:
        customer_message = "죄송합니다. 다시 한 번 이야기 해주세요"
        recommended_menu = []

    return customer_message, recommended_menu
