// 해시태그 및 페이지를 기준으로 메뉴를 업데이트하는 함수
function updateMenus(hashtags = "", page = 1) {
    $.ajax({
        url: '/orders/get_menus/',
        data: {hashtags: hashtags, page: page},
        dataType: 'json',
        success: function (data) {
            const menus = data.menus; // 서버로부터 받은 메뉴 데이터
            const user_hashtags = data.user_hashtags; // 사용자의 해시태그 목록
            const menuContainer = $('#menuContainer');
            menuContainer.empty(); // 메뉴 컨테이너 비우기

            const recommendedContainer = $('#recommendedContainer');
            recommendedContainer.empty(); // 추천 메뉴 컨테이너 비우기

            // 카테고리 버튼 생성
            const categoriesContainer = $('.categories .btn-group');
            categoriesContainer.empty();

            // 각 해시태그로 버튼 생성
            user_hashtags.forEach(tag => {
                const button = `
                    <button type="button" class="btn btn-custom-large" onclick="filterItems('${tag.hashtag}')">
                    ${tag.hashtag} 
                    </button>
                `;
                categoriesContainer.append(button);
            });
            console.log(menus)
            // 일반 메뉴 추가
            menus.forEach(menu => {
                const menuItem = `
                    <div class="menu-item card mb-3" onclick="addItem('${menu.food_name}', ${menu.price}, '${menu.img_url}', this, '${menu.food_name_ko}')">
                        <img src="${menu.img_url}" alt="${menu.food_name}" class="card-img-top">
                        <div class="card-body text-center">
                        <h5 class="card-title">${menu.food_name}</h5>
                        <p class="card-text text-muted">${menu.price}${won}</p>
                        </div>
                    </div>
                `;
                menuContainer.append(menuItem);
            });
            // 페이지네이션 버튼 업데이트
            updatePaginationButtons(data.page_count, page, hashtags);
        },
        error: function (error) {
            console.error('메뉴 업데이트 중 오류 발생:', error);
        }
    });
}

// 페이지네이션 버튼을 업데이트하는 함수
function updatePaginationButtons(totalPages, currentPage, hashtags) {
    const paginationButtons = $('#paginationButtons');
    paginationButtons.empty();

    // 각 페이지에 대한 버튼 생성
    for (let i = 1; i <= totalPages; i++) {
        const button = `<button class="btn btn-page mr-1" style="color: #47a2ce; border-color: #47a2ce;" onclick="changePage(${i}, '${hashtags}')">${i}</button>`;
        paginationButtons.append(button);
    }
}

// 페이지를 변경하는 함수
function changePage(pageNumber, hashtags) {
    updateMenus(hashtags, pageNumber); // 선택된 페이지로 메뉴 업데이트
}

// 해시태그에 따라 아이템을 필터링하는 함수
function filterItems(hashtags) {
    updateMenus(hashtags); // 선택된 해시태그로 메뉴 필터링
}
