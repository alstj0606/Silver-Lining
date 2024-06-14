const startButton = document.getElementById('startButton'); // 음성 인식 시작 버튼 요소
const transcription = document.getElementById('transcription'); // 음성 인식된 텍스트를 표시하는 요소

let currentUtterance = null; // 현재 음성 출력을 추적하는 변수

// 주어진 텍스트를 음성으로 출력합니다.
function speak(text, callback) {
    // 말풍선에 음성 내용 표시
    showSpeechBubble(text);

    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = languageCodeOut; // 출력 언어 설정
    utterance.rate = 1.5; // 예시로 1.5배 속도로 설정
    utterance.onend = function () {
        console.log("음성 안내가 끝났습니다.");

        // 음성 출력이 끝나면 말풍선을 제거하고 콜백 함수를 호출합니다.
        removeSpeechBubble();

        if (callback) {
            callback();
        }
    };
    synth.speak(utterance);
}

// 음성 출력을 나타내는 말풍선을 표시합니다.
function showSpeechBubble(text) {
    const speechBubbleContainer = document.querySelector('.speech-bubble');
    const speechBubble = document.createElement('div');
    speechBubble.className = 'speech-bubble-text';
    speechBubble.textContent = text;
    speechBubbleContainer.appendChild(speechBubble);
}

// 음성 출력 말풍선을 제거합니다.
function removeSpeechBubble() {
    const speechBubbleContainer = document.querySelector('.speech-bubble');
    const speechBubble = document.querySelector('.speech-bubble-text');
    if (speechBubble) {
        speechBubbleContainer.removeChild(speechBubble);
    }
}

// 음성 인식을 시작합니다.
function startSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("음성 인식이 지원되지 않는 브라우저입니다.");
    } else {
        const recognition = new webkitSpeechRecognition();
        recognition.lang = languageCodeIn; // 인식 언어 설정
        recognition.onstart = function () {
            // 인식 시작 시 스피너 표시
            startButton.innerHTML = '<div style="display: flex; align-items: center;">' +
                '<span class="spinner-border" style="width: 2.5rem; height: 2.5rem; margin-left: 10px;" role="status">' +
                '<span class="visually-hidden"></span>' +
                '</span>' +
                '<span>' + speechInputIn + '</span>' +
                '</div>';
        };

        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript; // 음성 인식 결과
            const csrfToken = getCsrfToken();
            axios.post('/orders/aibot/', {inputText: transcript}, {
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
                .then(function (response) {
                    const responseText = response.data.responseText; // AI 응답 텍스트
                    const recommended_menu = response.data.recommended_menu; // 추천 메뉴
                    AIMenus(recommended_menu); // 메뉴 업데이트
                    speak(responseText); // AI 응답 음성 출력
                })
                .catch(function (error) {
                    console.error('에러:', error);
                });
        };

        recognition.onend = function () {
            // 음성 인식 종료 시 버튼 텍스트 복구 및 클릭 이벤트 리스너 추가
            startButton.innerHTML = `
                <i class="fas fa-microphone-alt"></i>
                <span>${speechInput}</span>
                `;
            startButton.addEventListener('click', startSpeechRecognition);
        };

        recognition.start(); // 음성 인식 시작
    }
}

// 초기 이벤트 리스너 설정
document.getElementById('startButton').addEventListener('click', startSpeechRecognition);

// transcription 요소에 변화가 있을 때 플로팅 메시지 업데이트
transcription.addEventListener('input', function () {
    const text = transcription.textContent.trim();
});

function appendRecommendedMenuItems(container, items) {
    items.forEach(menu => {
        const menuItem = `
            <div class="menu-item card recommended" onclick="addItem('${menu.food_name}', ${menu.price}, '${menu.img_url}', this, '${menu.food_name_ko}')">
                <img src="${menu.img_url}" alt="${menu.food_name}" class="card-img-top">
                <div class="card-body text-center">
                    <h5 class="card-title">${menu.food_name}</h5>
                    <p class="card-text text-muted">${menu.price}${won}</p>
                </div>
            </div>
        `;
        container.append(menuItem);
    });
}

function appendMenuItems(container, items) {
    items.forEach(menu => {
        const menuItem = `
            <div class="menu-item card" onclick="addItem('${menu.food_name}', ${menu.price}, '${menu.img_url}', this, '${menu.food_name_ko}')">
                <img src="${menu.img_url}" alt="${menu.food_name}" class="card-img-top">
                <div class="card-body text-center">
                    <h5 class="card-title">${menu.food_name}</h5>
                    <p class="card-text text-muted">${menu.price}${won}</p>
                </div>
            </div>
        `;
        container.append(menuItem);
    });
}


// 추천 메뉴를 가져와 화면에 업데이트합니다.
function AIMenus(recommended_menu = "") {
    $.ajax({
        url: '/orders/aibot/',
        data: {recommended_menu: JSON.stringify(recommended_menu)},
        dataType: 'json',
        success: function (data) {
            const recommends = data.recommends; // 추천 메뉴 데이터
            const menuContainer = $('#menuContainer');
            const recommendedContainer = $('#recommendedContainer');
            const paginationButtons = $('#paginationButtons');

            menuContainer.empty();
            recommendedContainer.empty();
            paginationButtons.empty();
            if (Array.isArray(recommends)) {
                if (Array.isArray(recommends[0])) {
                    appendRecommendedMenuItems(recommendedContainer, recommends[0]); // 추천 메뉴 추가
                } else if (recommends[0] && typeof recommends[0] === 'object') {
                    appendRecommendedMenuItems(recommendedContainer, [recommends[0]]);
                } else {
                    console.error('Expected recommends[0] to be an array or object but got:', recommends[0]);
                }

                for (let i = 1; i < recommends.length; i++) {
                    if (Array.isArray(recommends[i])) {
                        appendMenuItems(menuContainer, recommends[i]); // 일반 메뉴 추가
                    } else if (recommends[i] && typeof recommends[i] === 'object') {
                        appendMenuItems(menuContainer, [recommends[i]]);
                    } else {
                        console.error('Expected recommends[' + i + '] to be an array or object but got:', recommends[i]);
                    }
                }
            } else {
                console.error('Expected recommends to be an array but got:', recommends);
            }
        },
        error: function (error) {
            console.error('메뉴 업데이트 중 오류 발생:', error);
        }
    });
}
