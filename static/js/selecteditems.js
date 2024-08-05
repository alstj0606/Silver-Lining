const selectedItems = {};  // 선택된 항목을 저장하는 객체

function addItem(name, price, imgUrl, element, food_name_ko) {
    if (!selectedItems[name]) {
        selectedItems[name] = {price: price, count: 1, imgUrl: imgUrl, food_name_ko: food_name_ko};  // 새로운 항목 추가
    } else {
        selectedItems[name].count += 1;  // 기존 항목의 수량 증가
    }
    updateSelectedItemsList();  // 선택된 항목 목록 업데이트
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
                <span>${item.price}${won}</span>
                <span>${item.count}${count}</span>
                </div>
                <button class="btn btn-lg" style="color:red;" onclick="removeItem('${name}')"> ${DelItem} </button>
            `;
        selectedItemsList.appendChild(itemElement);
        totalPrice += item.price * item.count;
    }
    document.getElementById('totalPrice').textContent = `${totalPrice}원`;  // 총 가격 업데이트
}

function removeItem(name) {
    if (selectedItems[name]) {
        delete selectedItems[name];  // 선택된 항목 제거
        updateSelectedItemsList();  // 선택된 항목 목록 업데이트
    }
}

function clearItems() {
    for (const key in selectedItems) {
        delete selectedItems[key];  // 모든 선택된 항목 제거
    }
    updateSelectedItemsList();  // 선택된 항목 목록 업데이트
}

function scrollSelectedItemsList(amount) {
    const selectedItemsList = document.getElementById('selectedItemsList');
    selectedItemsList.scrollBy({top: amount, behavior: 'smooth'});  // 선택된 항목 목록 스크롤
}

document.getElementById('submitOrderBtn').addEventListener('click', function () {
    const selectedItemsArray = Object.entries(selectedItems).map(([name, item]) => {
        return {name: name, count: item.count, food_name_ko: item.food_name_ko};  // 선택된 항목 배열로 변환
    });

    const totalPrice = calculateTotalPrice(selectedItems);  // 총 가격 계산

    // 주문 데이터를 JSON 문자열로 변환하여 전송
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
                xhr.setRequestHeader('X-CSRFToken', csrfToken);  // CSRF 토큰 설정
            } else {
                console.error('CSRF 토큰이 설정되지 않았습니다.');
                return false;
            }
        },
        success: function (data) {
            console.log('주문이 성공적으로 처리되었습니다.');
            window.location.href = '/orders/order_complete/' + data.order_number + '/';  // 주문 완료 페이지로 이동
        },
        error: function (error) {
            console.error('주문 처리 중 오류가 발생했습니다:', error);  // 오류 발생 시 메시지 출력
        }
    });
});

function calculateTotalPrice(selectedItems) {
    let totalPrice = 0;
    for (const item of Object.values(selectedItems)) {
        totalPrice += item.price * item.count;  // 선택된 항목의 가격 합산
    }
    return totalPrice;
}


