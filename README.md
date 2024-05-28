# 👩‍💻Project: Silver Lining
#### 내일배움캠프 AI 6기: 키오스크 페이지를 사용하기 어려운 노인들을 위한 키오스크 AI 서비스


<br>

## 👨‍🏫 Project Introduction (Team 8)


<br>

## 👨‍🏫 Developement Team (Pair Programming)
**박현준, 박소영, 박지현, 홍민서**
<br><br>
**Pair1: 박현준, 홍민서**
- 음성인식 파트 구현
- 메뉴추천 AI 메인로직 및 프롬프트 작성
- 비고령층 음성인식 주문 template 및 로직

**Pair2: 박지현, 박소영**
- 얼굴인식 파트 구현
- 고령층 키오스크 주문 template 및 로직
- Django Admin Page CRUD 및 Custom


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

#### (2) 고령층과 비고령층 주문단계 차별화
#### (2-1) 고령층
1. 고령층 주문 페이지 로딩과 동시에 출력되는 안내멘트 이후에 음성인식이 시작된다
2. 입력받은 음성데이터를 토대로 메뉴추천 AI가 추천메뉴를 띄워서 알려준다
3. 가장 추천되는 메뉴가 팝업창에 나타나고, 사용자는 이 메뉴를 장바구니에 넣거나 다른 추천 메뉴를 볼 수 있다

<br>

#### (2-2) 비고령층 (음성인식 주문 ver.)
1. 주문 방식을 음성인식으로 선택한 경우에 해당한다
2. 안내멘트에 따라 음성인식 버튼을 누르면 메뉴추천 AI와 장바구니 담기 등을 음성으로 진행할 수 있다
3. 고령층 주문단계와는 달리 자동으로 음성인식이 시작되는 것이 아니라 필요에 따라 원하는 주문과정에서 음성인식 기능을 ON/OFF로 사용할 수 있다

#### (2-3) 비고령층 (일반적인 키오스크 터치 주문 ver.)
1. 주문 방식을 화면터치로 선택한 경우에 해당한다
2. 일반적인 키오스크의 사용법처럼 주문과정을 터치로 진행할 수 있다
3. 별도의 음성인식 기능과 메뉴추천 AI기능은 제공하지 않는다

<br>

#### (2-4) 결제 이후 주문번호 배정
   - 앞선 2-1 ~ 2-3까지의 과정에서 공통적으로 제공되는 기능이다
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


<hr>

### 1. Auth
  - Allows users to register, log in, log out, modify their information, and withdraw membership.
  - Provides appropriate buttons based on user authentication status, such as 'Logout', 'Edit membership information', 'Withdraw membership', 'Login', and 'Sign up'.

### 2. Product_Post CRUD:
  - Enables users to create, read, update, and delete posts (including images) about items they want to sell.
  - Posts are accessible on the main page, full post list page, and can be viewed by non-members.
  - Allows navigation to detailed item pages by clicking on card links.

### 3. Comment CRD:
  - Provides functionality to create, read, and delete comments on posts.
  - Only allows comment authors to edit or delete their comments.

### 4. LIKE:
  - Allows users to like posts written by other users.
  - Users can like or unlike posts by clicking the heart symbol on the main page.


### 5. Profile Page & Follow:
  - Users can navigate to an author's profile page by clicking on their name.
  - Profiles display lists of posts made by the user and posts liked by the user, with hyperlinks to relevant post pages.
  - Includes a Follow button to follow or unfollow users.
  - Shows the number of followers and following users at the bottom of the Follow button.
     

## 📄 ERD:

