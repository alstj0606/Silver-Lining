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

    
        
    // 장바구니에 메뉴 추가
    function addItem(name, price, imgSrc, quantity) {
        // const username = 'mega'; // Replace with actual logic to get current username
        console.log("addItem name 들어오는지 >>>>>>", name) // 잘 찍히고 있음
        console.log("price 들어오는지 >>>>>", price) //
        console.log("imgSrc >>>>>", imgSrc) //

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
            cart[name] = JSON.stringify(item);
            console.log("else를 거친 cart[name] >>>> ", cart[name])
        }

        console.log("cart[name]으로 js 상의 수량이 잘 전달 되는지 >>>>> ", cart[name])

        let cartItem = JSON.parse(cart[name])

        axios.post('/orders/add_to_cart/', cartItem)
            .then(response => {
                console.log("장바구니 새로고침 해보기 >>>> ", cart)
                updateCartDisplay(response.data.cart_items);
            })
            .catch(error => {
                console.error('Error adding item to cart:', error);
            });
        }
        

    function submitOrder() {
        const selectedItems = Object.entries(cart).map(([name, item]) => ({
            name,
            count: item.count
        }));
    
        // Retrieve the total price directly from the DOM
        let totalPriceElement = document.getElementById('totalPrice');
        let currentTotal = parseInt(totalPriceElement.textContent.replace('총 가격: ', '', '원'), 10) || 0;
        console.log("submitOrder의 Selected Items >>>>", selectedItems)
        console.log("submitOrder의 currentTotal >>>>", currentTotal)
        axios.post('/orders/submit/', {
            items: selectedItems,
            total: currentTotal,
            username: 'mega'
        }).then(response => {
            alert('Order placed successfully');
            clearCart();
        }).catch(error => {
            console.error('Error submitting order:', error);
        });
    }
    
    function removeItem(name) {
        const username = 'mega';
        axios.post(`/cart/remove/${name}/`, { username })
            .then(response => {
                if (cart[name]) {
                    cart[name].count -= 1;
                    if (cart[name].count <= 0) delete cart[name];
                }
                updateCartDisplay();
            })
            .catch(error => {
                console.error('Error removing item from cart:', error);
            });
    }

    function clearCart() {
        const username = 'mega';
        axios.post('/cart/clear/', { username })
            .then(response => {
                cart = {};
                updateCartDisplay();
            })
            .catch(error => {
                console.error('Error clearing cart:', error);
            });
    }
    
    function submitOrder() {
        const selectedItems = Object.entries(cart).map(([name, item]) => ({
            name,
            count: item.count
        }));
    
        // Retrieve the total price directly from the DOM
        let totalPriceElement = document.getElementById('totalPrice');
        let currentTotal = parseInt(totalPriceElement.textContent.replace('총 가격: ', '', '원'), 10) || 0;
    
        axios.post('/orders/submit/', {
            items: selectedItems,
            total: currentTotal,
            username: 'mega'
        }).then(response => {
            alert('Order placed successfully');
            clearCart();
        }).catch(error => {
            console.error('Error submitting order:', error);
        });
    }


    function handleScrollArrows() {
        const cartItems = document.getElementById('cartItems');
        const upArrow = document.querySelector('.up-arrow');
        const downArrow = document.querySelector('.down-arrow');
    
        if (cartItems.scrollHeight > cartItems.clientHeight) {
            upArrow.style.display = 'block';
            downArrow.style.display = 'block';
        } else {
            upArrow.style.display = 'none';
            downArrow.style.display = 'none';
        }
    
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

