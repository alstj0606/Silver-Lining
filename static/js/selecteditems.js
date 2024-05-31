const selectedItems = {};  // 선택된 항목을 저장하는 객체

function addItem(name, price, imgUrl, element) {
    if (!selectedItems[name]) {
        selectedItems[name] = {price: price, count: 1, imgUrl: imgUrl};  // 새로운 항목 추가
    } else {
        selectedItems[name].count += 1;  // 기존 항목의 수량 증가
    }
    updateSelectedItemsList();  // 선택된 항목 목록 업데이트
    // flyToCart(element, document.getElementById('selectedItemsList'));  // 장바구니로 애니메이션 효과 추가
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
                <button class="btn btn-danger btn-lg" onclick="removeItem('${name}')"> ${del} </button>
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



function calculateTotalPrice(selectedItems) {
    let totalPrice = 0;
    for (const item of Object.values(selectedItems)) {
        totalPrice += item.price * item.count;  // 선택된 항목의 가격 합산
    }
    return totalPrice;
}


// 아쉽지만 관짝
// function flyToCart(element, targetElement) {
//     const imgToDrag = element.querySelector("img");
//     if (imgToDrag) {
//         const imgClone = imgToDrag.cloneNode(true);
//         let rect = imgToDrag.getBoundingClientRect();
//         imgClone.style.position = 'absolute';
//         imgClone.style.top = rect.top + 'px';
//         imgClone.style.left = rect.left + 'px';
//         imgClone.style.width = '250px'; // 초기 이미지 크기
//         imgClone.style.height = '250px'; // 초기 이미지 크기
//         imgClone.classList.add('fly-to-cart');
//         document.body.appendChild(imgClone);
//
//         // 🛒 아이콘 위치 설정
//         const cartIconRect = targetElement.getBoundingClientRect();
//
//         // 카트 아이콘 중앙 위치 계산
//         const cartCenterX = cartIconRect.left + cartIconRect.width / 2;
//         const cartCenterY = cartIconRect.top + cartIconRect.height / 2;
//
//         // 이미지 이동 속도 계산
//         const dx = (cartCenterX - rect.left) / 120; // x 방향 이동 속도
//         const dy = (cartCenterY - rect.top) / 120; // y 방향 이동 속도
//
//         // 이미지 크기 감소 속도 계산
//         const dw = (250 - 100) / 120; // 이미지 크기 감소 속도
//
//         // 이미지 이동 및 크기 조절 함수
//         function moveImage() {
//             rect = imgClone.getBoundingClientRect();
//             if ((dx > 0 && rect.left < cartCenterX) || (dx < 0 && rect.left > cartCenterX) ||
//                 (dy > 0 && rect.top < cartCenterY) || (dy < 0 && rect.top > cartCenterY)) {
//                 imgClone.style.left = (rect.left + dx) + 'px';
//                 imgClone.style.top = (rect.top + dy) + 'px';
//
//                 // 이미지 크기 조절
//                 const newWidth = parseFloat(imgClone.style.width) - dw;
//                 imgClone.style.width = newWidth + 'px';
//                 imgClone.style.height = newWidth + 'px';
//
//                 requestAnimationFrame(moveImage);
//             } else {
//                 imgClone.remove();
//             }
//         }
//
//         // 이미지 이동 시작
//         moveImage();
//     }
// }
