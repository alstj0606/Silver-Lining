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
                '<span>음성입력중</span>' +
                '<span class="spinner-border" style="width: 3rem; height: 3rem; margin-left: 10px;" role="status">' +
                '<span class="visually-hidden"></span>' +
                '</span>' +
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
                const hashtags = response.data.hashtags;
                const recommended_menu = response.data.recommended_menu;
                // console.log('서버 응답:', responseText);
                // console.log('추천 메뉴:', recommended_menu);
                updateMenus(hashtags, recommended_menu); // 메뉴 업데이트 먼저 실행
                speak(responseText);
            })
            .catch(function (error) {
                console.error('에러:', error);
            });
        };

        // 음성 인식 종료 시 버튼 텍스트 복구 및 클릭 이벤트 리스너 추가
        recognition.onend = function () {
            startButton.innerHTML = 'AI 음성인식';
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
