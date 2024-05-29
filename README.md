# 👩‍💻Project: Silver Lining
### "Every cloud has a silver lining."
#### 키오스크를 사용하기 어려운 고령층 소비자에게도 접근이 용이한 키오스크 AI 서비스.

<br>

## 👨‍🏫 Project Introduction (Team 8)
### 나이듦에 따른 신체의 노화가 단점으로 받아들여질 수 있는 상황에서 긍정적으로 생각해보자는 취지를 담은 프로젝트. 
- 키오스크 서비스에 접근하기 어려운 고령의 고객이 키오스크를 쉽게 이용할 수 있도록 구성한 서비스
- 얼굴 인식을 통해 키오스크를 이용하려는 사용자의 나이를 자동으로 파악하여 대상 연령대에 맞춘 UI/UX로 긍정적인 이용 경험 유도
- 음성 인식을 통한 AI 추천으로 고객에게 음성을 입력 받아 맞춤 메뉴 제안



<br>

## 👨‍🏫 Developement Team (Pair Programming)
**박현준, 박소영, 박지현, 홍민서**

<br><br>

**Pair1: 박현준, 홍민서**
- 키오스크 프론트엔드 작성
- 템플릿 음성인식 기능 구현
- AI메뉴 추천 모델 및 메뉴 필터링 기능
- 장바구니 담기, 결제 후 주문번호 출력 로직 작성

<br>

**Pair2: 박지현, 박소영**
- Django Admin Page 커스텀 (유저, 메뉴 CRUD)
- 얼굴인식 기능 구현
- 템플릿 레이아웃 구성
- 고령층 템플릿 구현 (음성인식 기능 결합)
- GPT프롬프트 수정


<br>

## ⏲️ Development time 
- 2024.05.13(월) ~ 2023.06.12(수)


<br>

## 💻 Development Environment
- **Programming Language** : Python 3.10
- **Web Framework** : DJANGO 4.2
- **Database** : SQLite (for development and testing), PostgreSQL (for Release)
- **IDE** : Visual Studio Code, Pycharm
- **Version Control** : Git, GitHub
- **Communication** : Zep, Slack, Figma, Zoom
  
<br>

## 📝 Project Result


<br>


## 📌 Key Features

### 1. 키오스크 사용자 
#### (1) 얼굴인식을 통한 연령층 식별과 키오스크 UI 맞춤화 
   - 키오스크에 내장된 카메라를 통해 키오스크 사용자의 얼굴 사진을 찍고, 사진에서 해당 사용자의 나이를 도출한다.
   - 도출해낸 나이가 고령층인 경우와 비고령층인 경우를 구분해서 키오스크 주문 UI를 맞춤화해서 제공한다.

<br>

#### (2) 고령층과 비고령층 주문단계 차별화
#### (2-1) 고령층
1. 고령층 주문 페이지 로딩과 동시에 출력되는 안내멘트 이후에 음성인식이 시작된다
2. 입력받은 음성데이터를 토대로 메뉴추천 AI가 추천메뉴를 띄워서 알려준다
3. 가장 추천되는 메뉴가 팝업창에 나타나고, 사용자는 이 메뉴를 장바구니에 넣거나 다른 추천 메뉴를 볼 수 있다


#### (2-2) 비고령층 (음성인식 주문 or 일반적인 키오스크 터치 주문)
1. 기본적으로는 일반적인 터치 주문 방식과 동일하게 사용할 수 있다
2. 안내멘트에 따라 음성인식 버튼을 누르면 메뉴추천 AI 기능을 음성인식으로 사용할 수 있다
3. 고령층 주문단계와는 달리 자동으로 음성인식이 시작되는 것이 아니라 필요에 따라 원하는 주문과정에서 음성인식 기능을 ON/OFF로 사용할 수 있다

<br>

#### (2-3) 결제 이후 주문번호 배정
   - 앞선 2-1 ~ 2-2까지의 과정에서 공통적으로 제공되는 기능이다
   - 하루마다 주문번호가 초기화된다

<br>

### 2. 점주 (staff)
#### (1) 메뉴 CRUD
- 메뉴 생성 전에 필요한 해시태그들을 미리 설정해줘야 한다
- 메뉴 생성시에는 메뉴 이름, 가격, 해시태그, 이미지를 업로드해야 한다
  
#### (2) 주문 현황 관련 (구현 예정)

<br><br>

### 3. 관리자 (superuser)
#### (1) staff CRUD 및 메뉴 CRUD
- 새로운 staff계정을 생성, 조회, 수정, 삭제할 수 있고, staff가 작성한 메뉴에 대해서도 관리자 차원에서 생성, 조회, 수정, 삭제를 할 수 있다
#### (2) staff에 permission 부여
- admin page내의 group을 새로 생성하여 staff가 메뉴 CRUD에만 접근가능하도록 제한한다

<br><br>
<hr>

## 📌 Key Features

### 1. Kiosk User

#### (1) Age Group Identification and Customized Kiosk UI through Facial Recognition

   - The kiosk, using its built-in camera, takes a photo of the kiosk user and estimates the user's age from the photo.

   - Depending on whether the estimated age indicates an older user or a younger user, the kiosk order UI will be customized accordingly.


<br>

#### (2) Differentiation in Order Steps for Older and Younger Users


#### (2-1) Older Users

1. As soon as the order page for older users loads, a guide message is played and the voice recognition begins.

2. Based on the voice data received, the AI menu recommendation system displays suggested menus.

3. The top recommended menu appears in a popup, and the user can choose to add this menu to the cart or view other recommended menus.



#### (2-2) Younger Users (Voice Recognition Order or Touch-screen Order)

1. By default, users can use the typical tap-to-order method.

2. Users can activate the AI menu recommendation feature using voice recognition by tapping the voice recognition button, as instructed by the guide message.

3. Unlike the order process for older users, voice recognition does not start automatically; users can turn the voice recognition feature on or off as needed during the ordering process.



<br>



#### (2-3) Assigning Order Numbers Post Payment

   - Both of the order process of older and younger user go through this process

   - Order numbers that are given to the customers are reset daily.


<br>


### 2. Store Owner (Staff)

#### (1) Menu CRUD

- Predefined hashtags need to be set before menu creation.

- When creating a menu, the menu name, price, hashtags, and images must be uploaded.

  

#### (2) Order Status Related (work in progress)



<br><br>



### 3. Admin (Superuser)

#### (1) Staff CRUD and Menu CRUD

- The admin can create, view, edit, and delete staff accounts as well as the menus created by staff members.

#### (2) Assigning Permissions to Staff

- Through the admin page, a new group can be created so that staff members are restricted to only performing menu CRUD operations.

<br>
     

## 📄 ERD:
![SivlerLining (2)](https://github.com/billyhyunjun/Silver-Lining/assets/159408752/7ef6181b-7b38-4a7c-ae2f-6d6d880f0197)

