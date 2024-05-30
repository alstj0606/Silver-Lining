
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

### 요청을 파악해야 함

def request_type(client, input_text, current_user):
    print("\n\n\n request_type 진입 \n\n\n")
    print("\n\n input text \n\n", input_text)
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
        You are a distinguisher of the input text whether it is request for a menu recommendation, or an alteration on the cart, or moving on to the payment process.
        """

    system_output = f"""
        Choose the input text type from the three categories I suggest: "menu", "cart", "pay".
        You should also include the input_text in the format of Input: input_text.
        If the category is cart, extract the menu, requested number of menus, and the performance to proceed with the cart such as adding, editing, or deleting.
        For the cart, response should include category, input text and the list of three options I suggested above.
        """

    client = OpenAI(api_key=settings.OPEN_API_KEY)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_data},
            {"role": "system", "content": system_output},
            {"role": "user", "content": input_text},
        ],
    )

    print("AI 응답 >>>>>>>>>>>>>>>>>>> ", completion)
    ai_response = completion.choices[0].message.content
    print(ai_response)
    ## Input: 아메리카노 두 잔 넣어 줘
    ## Category: cart
    # category -> 결과값에 따라서 어느 ai 로 보낼건지: 
    """
    메뉴 추천이면 bot() -> 메뉴 추천, 메시지 -> 음성 메시지 출력, 추천 메뉴 보여주기
    장바구니면 bot2() -> 대상, 행동을 input에서 뽑아낸다(아메리카노/ 개수 / 넣는 거) ->  대상: 아메리카노, 개수: 2개, 행동: 넣는 거 ---(js로 넣어줄 수 있나?)---> 눌러주면 되는 것
    아메리카노/ 2개/ 넣는 거 --> views.py ? orderbot --> views.py post() db 아메리카노, 2잔 추가 --> 
    
    responseText, category

    views.py:
            if category == cart:
                responseText --> 쪼개는거: 메뉴, 개수, 행위
            elif == menu:
                response ? ? ? 다시 음성인식 speak() -> speechRecognition() - >
            category - cart --> 
            category - menu -->
            category - pay -->
    """
    return ai_response


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

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": f"Recommended Menu: {', '.join(recommended_menu)}"},
        ],
    )

    ai_response = completion.choices[0].message.content
    customer_message = ""

    try:
        for line in ai_response.split('\n'):
            line = line.strip()  # Remove whitespace from both ends
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


### 카트 타입이 들어옴 inputText 받아서
### gpt 돌리는 것: 메뉴 뽑고, 개수 뽑고, 행동 뽑고
### 메뉴/ 개수/ 행동  각각 변수에 넣어서 return
### "아이스 아메리카노 두잔 넣어줘" 이런 텍스트를 받았는데