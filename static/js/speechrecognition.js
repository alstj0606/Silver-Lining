const startButton = document.getElementById('startButton');
const transcription = document.getElementById('transcription');


function speak(text, callback) {
    // Create and show the speech bubble
    showSpeechBubble(text);

    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ko-KR';
    utterance.onend = function () {
        console.log("음성 안내가 끝났습니다.");

        // Remove the speech bubble when speech ends
        removeSpeechBubble();

        if (callback) {
            callback();
        }
    };
    synth.speak(utterance);
}

function showSpeechBubble(text) {
    const speechBubbleContainer = document.querySelector('.speech-bubble');
    const speechBubble = document.createElement('div');
    speechBubble.className = 'speech-bubble-text';
    speechBubble.textContent = text;
    speechBubbleContainer.appendChild(speechBubble);
}

function removeSpeechBubble() {
    const speechBubbleContainer = document.querySelector('.speech-bubble');
    const speechBubble = document.querySelector('.speech-bubble-text');
    if (speechBubble) {
        speechBubbleContainer.removeChild(speechBubble);
    }
}


function startSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("음성 인식이 지원되지 않는 브라우저입니다.");
    } else {
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'ko-KR';

        // 음성 인식 시작 시 스피너 표시
        recognition.onstart = function () {
            startButton.innerHTML = '<div style="display: flex; align-items: center;">' +
                '<span class="spinner-border" style="width: 2.5rem; height: 2.5rem; margin-left: 10px;" role="status">' +
                '<span class="visually-hidden"></span>' +
                '</span>' +
                '<span>  음성입력중</span>' +
                '</div>';
        };

        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript;
            const csrfToken = getCsrfToken();
            axios.post('/orders/aibot/', {inputText: transcript}, {
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
                .then(function (response) {
                    const responseText = response.data.responseText;
                    const recommended_menu = response.data.recommended_menu;
                    AIMenus(recommended_menu); // 메뉴 업데이트 먼저 실행
                    speak(responseText);
                })
                .catch(function (error) {
                    console.error('에러:', error);
                });
        };

        // 음성 인식 종료 시 버튼 텍스트 복구 및 클릭 이벤트 리스너 추가
        recognition.onend = function () {
            startButton.innerHTML = `
                <i class="fas fa-microphone-alt"></i> <!-- 이모티콘 추가 -->
                <span>AI 음성입력</span>
            `;
            startButton.addEventListener('click', startSpeechRecognition);
        };

        recognition.start();
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
            <div class="menu-item card recommended" onclick="addItem('${menu.food_name}', ${menu.price}, '${menu.img_url}', this)">
                <img src="${menu.img_url}" alt="${menu.food_name}" class="card-img-top">
                <div class="card-body text-center">
                    <h5 class="card-title text-primary">${menu.food_name}</h5>
                    <p class="card-text text-muted">${menu.price}원</p>
                </div>
            </div>
        `;
        container.append(menuItem);
    });
}

function appendMenuItems(container, items) {
    items.forEach(menu => {
        const menuItem = `
            <div class="menu-item card" onclick="addItem('${menu.food_name}', ${menu.price}, '${menu.img_url}', this)">
                <img src="${menu.img_url}" alt="${menu.food_name}" class="card-img-top">
                <div class="card-body text-center">
                    <h5 class="card-title text-primary">${menu.food_name}</h5>
                    <p class="card-text text-muted">${menu.price}원</p>
                </div>
            </div>
        `;
        container.append(menuItem);
    });
}

function AIMenus(recommended_menu = "") {
    $.ajax({
        url: '/orders/aibot/',
        data: {recommended_menu: JSON.stringify(recommended_menu)},
        dataType: 'json',
        success: function (data) {
            const recommends = data.recommends;
            const menuContainer = $('#menuContainer');
            const recommendedContainer = $('#recommendedContainer');
            const paginationButtons = $('#paginationButtons');

            menuContainer.empty();
            recommendedContainer.empty();
            paginationButtons.empty();
            if (Array.isArray(recommends)) {
                if (Array.isArray(recommends[0])) {
                    appendRecommendedMenuItems(recommendedContainer, recommends[0]);
                } else if (recommends[0] && typeof recommends[0] === 'object') {
                    appendRecommendedMenuItems(recommendedContainer, [recommends[0]]);
                } else {
                    console.error('Expected recommends[0] to be an array or object but got:', recommends[0]);
                }

                for (let i = 1; i < recommends.length; i++) {
                    if (Array.isArray(recommends[i])) {
                        appendMenuItems(menuContainer, recommends[i]);
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
