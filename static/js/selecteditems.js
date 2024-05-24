const selectedItems = {};

function addItem(name, price, imgUrl, element) {
    if (!selectedItems[name]) {
        selectedItems[name] = {price: price, count: 1, imgUrl: imgUrl};
    } else {
        selectedItems[name].count += 1;
    }
    updateSelectedItemsList();
    flyToCart(element, document.getElementById('selectedItemsList'));
}

function updateSelectedItemsList() {
    const selectedItemsList = document.getElementById('selectedItemsList');
    selectedItemsList.innerHTML = '';
    let totalPrice = 0;
    for (const [name, item] of Object.entries(selectedItems)) {
        const itemElement = document.createElement('div');
        itemElement.classList.add('selected-item');
        itemElement.innerHTML = `
                <img src="${item.imgUrl}" alt="${name}">
                <div>
                <span>${name}</span>
                <span>${item.price}원</span>
                <span>${item.count}개</span>
                </div>
                <button class="btn btn-danger btn-lg" onclick="removeItem('${name}')">삭제</button>
            `;
        selectedItemsList.appendChild(itemElement);
        totalPrice += item.price * item.count;
    }
    document.getElementById('totalPrice').textContent = `${totalPrice}원`;
}

function removeItem(name) {
    if (selectedItems[name]) {
        delete selectedItems[name];
        updateSelectedItemsList();
    }
}

function clearItems() {
    for (const key in selectedItems) {
        delete selectedItems[key];
    }
    updateSelectedItemsList();
}

function flyToCart(element, targetElement) {
    const imgToDrag = element.querySelector("img");
    if (imgToDrag) {
        const imgClone = imgToDrag.cloneNode(true);
        let rect = imgToDrag.getBoundingClientRect();
        imgClone.style.position = 'absolute';
        imgClone.style.top = rect.top + 'px';
        imgClone.style.left = rect.left + 'px';
        imgClone.style.width = '250px'; // 초기 이미지 크기
        imgClone.style.height = '250px'; // 초기 이미지 크기
        imgClone.classList.add('fly-to-cart');
        document.body.appendChild(imgClone);

        // 🛒 아이콘 위치 설정
        const cartIconRect = targetElement.getBoundingClientRect();

        // 카트 아이콘 중앙 위치 계산
        const cartCenterX = cartIconRect.left + cartIconRect.width / 2;
        const cartCenterY = cartIconRect.top + cartIconRect.height / 2;

        // 이미지 이동 속도 계산
        const dx = (cartCenterX - rect.left) / 120; // x 방향 이동 속도
        const dy = (cartCenterY - rect.top) / 120; // y 방향 이동 속도

        // 이미지 크기 감소 속도 계산
        const dw = (250 - 100) / 120; // 이미지 크기 감소 속도

        // 이미지 이동 및 크기 조절 함수
        function moveImage() {
            rect = imgClone.getBoundingClientRect();
            if ((dx > 0 && rect.left < cartCenterX) || (dx < 0 && rect.left > cartCenterX) ||
                (dy > 0 && rect.top < cartCenterY) || (dy < 0 && rect.top > cartCenterY)) {
                imgClone.style.left = (rect.left + dx) + 'px';
                imgClone.style.top = (rect.top + dy) + 'px';

                // 이미지 크기 조절
                const newWidth = parseFloat(imgClone.style.width) - dw;
                imgClone.style.width = newWidth + 'px';
                imgClone.style.height = newWidth + 'px';

                requestAnimationFrame(moveImage);
            } else {
                imgClone.remove();
            }
        }

        // 이미지 이동 시작
        moveImage();
    }
}

function scrollSelectedItemsList(amount) {
    const selectedItemsList = document.getElementById('selectedItemsList');
    selectedItemsList.scrollBy({top: amount, behavior: 'smooth'});
}

document.getElementById('submitOrderBtn').addEventListener('click', function () {
    const selectedItemsArray = Object.entries(selectedItems).map(([name, item]) => {
        return {name: name, count: item.count};
    });

    const totalPrice = calculateTotalPrice(selectedItems);

    // 요청 데이터를 JSON 문자열로 변환하여 전송
    $.ajax({
        url: '/orders/get_menus/',
        cache: false,
        dataType: 'json',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({items: selectedItemsArray, total_price: totalPrice}),
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


function calculateTotalPrice(selectedItems) {
    let totalPrice = 0;
    for (const item of Object.values(selectedItems)) {
        totalPrice += item.price * item.count;
    }
    return totalPrice;
}
