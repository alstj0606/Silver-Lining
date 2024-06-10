let cart = {};

    // 장바구니 조회
    function updateCartDisplay(cartData) {
        let currentTotal = 0;
        cartItems.innerHTML = '';
        console.log("cart 확인해보기 >>>>> ", cartData)
        for (let name in cartData) {
            let item = cartData[name];
            // string으로 넘어왔을 경우
            if (typeof item === 'string') {
                item = JSON.parse(item);
            }
            if (typeof item === 'object') {
                console.log("Parsed item >>>", JSON.stringify(item));
                console.log("item 출력 >>>> ", item)

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
        axios.get('/orders/cart/')
        .then(response => {
            const cartData = response.data.cart_items ? response.data.cart_items : {};
            console.log("cartData type >>>", typeof cartData)
            console.log("cartData here >>>>> ",cartData)
            updateCartDisplay(cartData);
        })
        .catch(error => {
            console.error('카트 데이터 fetch 실패:', error);
        });
    }


    // 장바구니에 메뉴 추가
    function addItem(name, price, imgSrc, quantity) {
        console.log("addItem name 들어오는지 >>>>>>", name) // 잘 찍히고 있음
        console.log("price 들어오는지 >>>>>", price) //
        console.log("imgSrc >>>>>", imgSrc) //
        console.log("quantity >>>>", quantity)
        console.log("레모네이드 10개 아니라고... >>>", cart[name])
        let item = {
            menu_name: name,
            price: price,
            quantity: quantity,
            image: imgSrc
        };
        if (cart[name]) {
            let existingItem = JSON.parse(cart[name]);
            existingItem.quantity += 1;
            cart[name] = JSON.stringify(existingItem);
            console.log("existingItem 을 거친 cart[name]", cart[name])
        } else {
            item.quantity = 1
            cart[name] = JSON.stringify(item);
            console.log("else를 거친 cart[name] >>>> ", cart[name])
        }

        console.log("cart[name]으로 js 상의 수량이 잘 전달 되는지 >>>>> ", cart[name])

        let cartItem = JSON.parse(cart[name])

        axios.post('/orders/add_to_cart/', cartItem)
            .then(response => {
                console.log("Unexpected Response Data Format >>>")
                console.log("장바구니 새로고침 해보기 >>>> ", cart)
                refreshCart();
            })
            .catch(error => {
                console.error('Error adding item to cart:', error);
            });
        }

    function getCsrfToken() {
        const csrfTokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return csrfTokenElement ? csrfTokenElement.value : null;
    }

    const csrfToken = getCsrfToken();
    console.log("csrfToken 정의 이후 바로 >>>>", csrfToken)

    function submitOrder() {
        console.log("submitOrder >>>>>>> ")
        const csrfToken = getCsrfToken();
        const selectedItems = Object.entries(cart).map(([name, item]) => {
            item = JSON.parse(item)
            return {name: name, count: item.quantity, food_name_ko: item.menu_name};
        });
        console.log("원하는 형태의 selectedItems 인지 >>>> ", selectedItems)

        // Retrieve the total price directly from the DOM
        let totalPriceElement = document.getElementById('totalPrice');
        let currentTotal = parseInt(totalPriceElement.textContent.replace('총 가격: ', '', '원'), 10) || 0;
        console.log("submitOrder의 Selected Items >>>>", selectedItems)
        console.log("submitOrder의 currentTotal >>>>", currentTotal)
        console.log("csrftoken 가져와지는지 >>>> ", csrfToken)
        console.log("axios post data >>>>>>> ")

        axios.post("/orders/submit/", JSON.stringify({
            items: selectedItems,
            total: currentTotal
        }), {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        }).then(response => {
            console.log("submitorder 후 data >>> ", response.data)
            window.location.href = '/orders/order_complete/' + response.data.order_number + '/';
        }).catch(error => {
            console.error('Error submitting order:', error);
        });
    }

    function removeItem(name) {
        const csrfToken = getCsrfToken();
        console.log("menu_name 받아와지는지 >>>> ", name)
        axios.post(`/orders/cart/remove/${name}/`, {},
            {headers: {
                'X-CSRFToken': csrfToken
            }})
            .then(response => {
                console.log("cart[name] >>>>>> ", cart[name])
                delete cart[name];
                console.log("cart[name] 2번째 >>>>>> ", cart[name])
                refreshCart();
            })
            .catch(error => {
                console.error('Error removing item from cart:', error);
            });
    }

    function clearCart() {
        console.log("clearCart 진입했는지")
        axios.post('/orders/cart/clear/', {},
        {headers: {
            'X-CSRFToken': csrfToken
        }})
            .then(response => {
                cart = {};
                refreshCart();
            })
            .catch(error => {
                console.error('Error clearing cart:', error);
            });
    }




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

    // Invoke handleScrollArrows on page load to set initial arrow states
    handleScrollArrows();

