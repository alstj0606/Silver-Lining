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


def get_recommended_menus(client, input_text, current_user):
    # 사용자의 카테고리 가져오기
    category = current_user.category

    # 사용자의 메뉴 및 해시태그  가져오기
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
        "Recommended Menu: [menu_name]"
        For the "Recommended Menu" section, select three options that are most closely related to the customer's request and rank them accordingly.
        The main format of recommended menu should be "Recommended Menu: menu_name, menu_name, menu_name".
        The output of recommended menus must include three items. If fulfilling three items is difficult to achieve, go through the menu table to find the closest menu possible.
        It would be easier for you to consider hashtags when finding related menu.
        When there are more than one keyword that you take into account, you should prioritize the keyword that is related to the menu.
        For example, when the customer asks for 'iced coffee', you should consider the menu that is 'coffee', rather than 'iced' beverages.
        """
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_data},
            {"role": "system", "content": system_output},
            {"role": "user", "content": input_text},
        ],
    )

    ai_response = completion.choices[0].message.content
    recommended_menu = []

    try:
        for line in ai_response.split('\n'):
            line = line.strip()  # Remove whitespace from both ends
            if line.startswith('Recommended Menu:'):
                recommended_menu = line.split('Recommended Menu: ')[1].strip().split(', ')
                break  # We don't need to continue once we have extracted the recommended menus

    except IndexError:
        recommended_menu = []

    print("recommended_men >>>>>>>", recommended_menu)
    return recommended_menu


def generate_final_response(client, recommended_menu, current_user):
    system_instructions = f"""
        When delivering a message to the customer,
        kindly determine their desired menu item and keep the message concise, preferably to one sentence.
        The message you respond must include the menu name of recommended_menu[0].
        The message must be in Korean, and think that you are having a small talk with your customer.
        There should not be a greetings, though.
        The format of the data I desire as a result is:
        "Message: [content]
        Recommended Menu: {', '.join(recommended_menu)}"
        """

    # OpenAI API로 요청을 보냅니다.
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": f"Recommended Menu: {', '.join(recommended_menu)}"},
        ],
    )

    # OpenAI 응답을 처리합니다.
    ai_response = completion.choices[0].message.content
    customer_message = ""

    try:
        for line in ai_response.split('\n'):
            line = line.strip()  # 양쪽 공백 제거
            if line.startswith('Message:'):
                customer_message = line.split('Message: ')[1].strip()
                break  # We don't need to continue once we have extracted the customer message

    except IndexError:
        customer_message = "죄송합니다. 다시 한 번 이야기 해주세요"

    print("customer_message >>>>>>>>>>>>", customer_message)
    return customer_message


def bot(request, input_text, current_user):
    client = OpenAI(api_key=settings.OPEN_API_KEY)

    # Getting the recommended menus
    recommended_menu = get_recommended_menus(client, input_text, current_user)

    # Generating the final response
    customer_message = generate_final_response(client, recommended_menu, current_user)

    return customer_message, recommended_menu
