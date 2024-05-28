function updateMenus(hashtags = "", page = 1) {
    $.ajax({
        url: '/orders/get_menus/',
        data: {hashtags: hashtags, page: page},
        dataType: 'json',
        success: function (data) {
            const menus = data.menus;
            const hashtags = data.hashtags;
            const user_hashtags = data.user_hashtags;
            const menuContainer = $('#menuContainer');
            menuContainer.empty();

            const recommendedContainer = $('#recommendedContainer');
            recommendedContainer.empty();

            // 카테고리 버튼 생성
            const categoriesContainer = $('.categories .btn-group');
            categoriesContainer.empty();

            // 각 해시태그로 버튼 생성
            user_hashtags.forEach(tag => {
                const button = `
                    <button type="button" class="btn btn-primary btn-custom-large" onclick="filterItems('${tag.hashtag}')">
                    ${tag.hashtag} 
                    </button>
                `;
                categoriesContainer.append(button);
            });

            // 일반 메뉴 추가
            menus.forEach(menu => {
                const menuItem = `
                            <div class="menu-item card mb-3" onclick="addItem('${menu.food_name}', ${menu.price}, '${menu.img_url}', this)">
                                <img src="${menu.img_url}" alt="${menu.food_name}" class="card-img-top">
                                <div class="card-body text-center">
                                    <h5 class="card-title text-primary">${menu.food_name}</h5>
                                    <p class="card-text text-muted">${menu.price}원</p>
                                </div>
                            </div>
                        `;
                menuContainer.append(menuItem);
            });
            updatePaginationButtons(data.page_count, page, hashtags);
        },
        error: function (error) {
            console.error('메뉴 업데이트 중 오류 발생:', error);
        }
    });
}

function updatePaginationButtons(totalPages, currentPage, hashtags) {
    const paginationButtons = $('#paginationButtons');
    paginationButtons.empty();

    for (let i = 1; i <= totalPages; i++) {
        const button = `<button class="btn btn-outline-primary btn-page mr-1" onclick="changePage(${i}, '${hashtags}')">${i}</button>`;
        paginationButtons.append(button);
    }
}

function changePage(pageNumber, hashtags) {
    updateMenus(hashtags, pageNumber);
}

function filterItems(hashtags) {
    updateMenus(hashtags);
}