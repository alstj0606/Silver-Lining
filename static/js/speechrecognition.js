    function speak(text, callback) {
        const synth = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'ko-KR';
        utterance.onend = function () {
            console.log("음성 안내가 끝났습니다.");
            if (callback) {
                callback();
            }
        };
        synth.speak(utterance);
    }

    function startSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window)) {
            alert("음성 인식이 지원되지 않는 브라우저입니다.");
        } else {
            const recognition = new webkitSpeechRecognition();
            recognition.lang = 'ko-KR';
            recognition.start();
            recognition.onresult = function (event) {
                const transcript = event.results[0][0].transcript;
                transcription.textContent = transcript;
                const csrfToken = getCsrfToken();
                axios.post('{% url "orders:aibot" %}', {inputText: transcript}, {
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                })
                    .then(function (response) {
                        const responseText = response.data.responseText;
                        const hashtags = response.data.hashtags;
                        console.log('서버 응답:', responseText);
                        updateMenus(hashtags); // 메뉴 업데이트 먼저 실행
                        speak(responseText, startSpeechRecognition); // 그 다음에 음성 안내 실행
                    })
                    .catch(function (error) {
                        console.error('에러:', error);
                    });
            };
            recognition.onend = function () {
                startButton.textContent = '음성 입력 다시 시작';
            };
        }
    }