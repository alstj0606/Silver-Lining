let cart = {};

    function addItem(name, price, imgSrc) {
        // If item already in cart, increment count, otherwise add new item
        if (cart[name]) {
            cart[name].count += 1;
        } else {
            cart[name] = { price: price, count: 1, imgSrc: imgSrc };
        }
        updateCartDisplay();
    }

    function updateCartDisplay() {
        let cartItems = document.getElementById('cartItems');
        cartItems.innerHTML = ''; // Clear the cart display
        let currentTotal = 0;

        for (let name in cart) {
            let item = cart[name];
            currentTotal += item.price * item.count;
            cartItems.innerHTML += `
                <div class="cart-item">
                    <img src="${item.imgSrc}" alt="${name}">
                    <span>${name}</span>
                    <span>${item.price}원</span>
                    <span>${item.count}개</span>
                    <button class="remove" onclick="removeItem('${name}')">삭제</button>
                </div>`;
        }

        // Update total price
        document.getElementById('totalPrice').textContent = `총 가격: ${currentTotal}원`;
        handleScrollArrows();
    }

    function removeItem(name) {
        if (cart[name]) {
            cart[name].count -= 1;
            if (cart[name].count <= 0) delete cart[name];
        }

        updateCartDisplay();
    }

    document.getElementById('clearCartBtn').addEventListener('click', function() {
        cart = {}; // Clear the cart
        updateCartDisplay(); // Update the UI to reflect the cleared cart
});


// Handle visibility of the arrow buttons

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
    handleScrollArrows(); // Update the arrows' visibility based on scroll position
});



document.querySelector('.down-arrow').addEventListener('click', function() {
    const cartItems = document.getElementById('cartItems');
    cartItems.scrollTop += 50;
    handleScrollArrows(); // Update the arrows' visibility based on scroll position
});

// Invoke handleScrollArrows on page load to set initial arrow states
handleScrollArrows();


document.getElementById('submitOrderBtn').addEventListener('click', function () {
    const selectedItemsArray = Object.entries(cart).map(([name, item]) => {
        return {name: name, count: item.count};
    });
    console.log(selectedItemsArray)
    // Retrieve the total price directly from the DOM
    let totalPriceElement = document.getElementById('totalPrice');
    let currentTotal = parseInt(totalPriceElement.textContent.replace('총 가격: ', '', '원'), 10) || 0;

    // 요청 데이터를 JSON 문자열로 변환하여 전송
    $.ajax({
        url: '/orders/get_menus/',
        cache: false,
        dataType: 'json',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({items: selectedItemsArray, total_price: currentTotal}),
        beforeSend: function (xhr) {
            const csrfToken = getCsrfToken();
            if (csrfToken) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            } else {
                console.error('CSRF 토큰이 설정되지 않았습니다.');
                return false;
            }
        },
        success: function (data) {
            console.log('주문이 성공적으로 처리되었습니다.');
            window.location.href = '/orders/order_complete/' + data.order_number + '/';
        },
        error: function (error) {
            console.error('주문 처리 중 오류가 발생했습니다:', error);
        }
    });
});