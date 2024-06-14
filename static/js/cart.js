let cartData = {};

    // 장바구니 조회
    function updateCartDisplay(cartData) {
        let currentTotal = 0;
        cartItems.innerHTML = '';
        for (let name in cartData) {
            let item = cartData[name];
            // string으로 넘어왔을 경우
            if (typeof item === 'string') {
                item = JSON.parse(item);
            }
            if (typeof item === 'object') {

                    if (item["price"] !== undefined) {
                        currentTotal += item["price"] * item["quantity"];

                        cartItems.innerHTML += `
                            <div class="cart-item">
                                <img src="${item["image"]}">
                                <span>${item["menu_name"]}</span>
                                <span>${item["price"]}원</span>
                                <span>${item["quantity"]}개</span>
                                <button class="remove" onclick="removeItem('${item["menu_name"]}')">삭제</button>
                            </div>`;
                    }

                }
        }
        document.getElementById('totalPrice').textContent = `총 가격: ${currentTotal}원`;
        handleScrollArrows();
        }


    function refreshCart() {
        return axios.get('/orders/cart/')
            .then(response => {
                const cartData = response.data.cart_items ? response.data.cart_items : {};
                updateCartDisplay(cartData);
                return cartData;
            })
            .catch(error => {
                console.error('카트 데이터 fetch 실패:', error);
                return {}; // 오류 발생 시 빈 객체 반환
            });
    }


    // 장바구니에 메뉴 추가
    function addItem(name, price, imgSrc, quantity) {
        let item = {
            menu_name: name,
            price: price,
            quantity: quantity,
            image: imgSrc
        };
        if (cartData[name]) {
            let existingItem = JSON.parse(cartData[name]);
            if (typeof existingItem === 'string') { 
                existingItem = JSON.parse(existingItem); 
            } 
            existingItem.quantity += 1;
            cartData[name] = JSON.stringify(existingItem);
        } else {
            item.quantity = 1
            cartData[name] = JSON.stringify(item);
        }

        let cartItem = JSON.parse(cartData[name])

        axios.post('/orders/add_to_cart/', cartItem)
            .then(response => {
                console.log("Unexpected Response Data Format >>>")
                console.log("장바구니 새로고침 해보기 >>>> ", cartData)
                refreshCart();
            })
            .catch(error => {
                if (error.response) {
                    // 서버에서 응답이 돌아온 경우
                    console.error('Error response:', error.response.data);
                    console.error('Status code:', error.response.status);
                    console.error('Headers:', error.response.headers);
                } else if (error.request) {
                    // 요청이 만들어졌으나 응답을 받지 못한 경우
                    console.error('Error request:', error.request);
                } else {
                    // 요청 설정 중에 에러가 발생한 경우
                    console.error('Error message:', error.message);
                }
                console.error('Error config:', error.config);
            })};

    function getCsrfToken() {
        const csrfTokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return csrfTokenElement ? csrfTokenElement.value : null;
    }


    function submitOrder() {
        const csrfToken = getCsrfToken();

        refreshCart().then(cartData => {
            console.log("Received cartData from refreshCart >>>>>>> ", cartData);

            // 각 아이템을 JSON 파싱 후 올바른 형식으로 변환
            const selectedItems = Object.entries(cartData).map(([name, item]) => {
                console.log(`Parsing item: ${item}`); // 각 item을 파싱하기 전 로그 출력
                if (typeof item === 'string') {
                    item = JSON.parse(item);
                }
                return {
                    id: item.item_id,
                    food_name_ko: item.menu_name,
                    count: item.quantity
                };
            });

            // 총 가격 가져오기
            let totalPriceElement = document.getElementById('totalPrice');
            let currentTotal = parseInt(totalPriceElement.textContent.replace('총 가격: ', '').replace('원', ''), 10) || 0;

            // Axios 요청
            axios.post("/orders/submit/", {
                items: selectedItems,
                total: currentTotal
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            }).then(response => {
                window.location.href = '/orders/order_complete/' + response.data.order_number + '/';
            }).catch(error => {
                console.error('Error submitting order:', error);
            });
        });
    }

    // 장바구니에서 메뉴 삭제
    function removeItem(name) {
        const csrfToken = getCsrfToken();
        axios.post(`/orders/cart/remove/${name}/`, {},
            {headers: {
                'X-CSRFToken': csrfToken
            }})
            .then(response => {
                delete cartData[name];
                refreshCart();
            })
            .catch(error => {
                console.error('Error removing item from cart:', error);
            });
    }

    // 장바구니 전체 메뉴 삭제
    function clearCart() {
        const csrfToken = getCsrfToken();
        axios.post('/orders/cart/clear/', {},
        {headers: {
            'X-CSRFToken': csrfToken
        }})
            .then(response => {
                cartData = {};
                refreshCart();
            })
            .catch(error => {
                console.error('Error clearing cart:', error);
            });
    }

    // 장바구니 스크롤
    function handleScrollArrows() {
        const cartItems = document.getElementById('cartItems');
        const upArrow = document.querySelector('.up-arrow');
        const downArrow = document.querySelector('.down-arrow');

        upArrow.disabled = cartItems.scrollTop === 0;
        downArrow.disabled = cartItems.scrollTop >= (cartItems.scrollHeight - cartItems.clientHeight);
    }

    document.querySelector('.up-arrow').addEventListener('click', function() {
        const cartItems = document.getElementById('cartItems');
        cartItems.scrollTop -= 50;
        handleScrollArrows();
    });

    document.querySelector('.down-arrow').addEventListener('click', function() {
        const cartItems = document.getElementById('cartItems');
        cartItems.scrollTop += 50;
        handleScrollArrows();
    });

    handleScrollArrows();