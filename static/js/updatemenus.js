function updateMenus(hashtags = "", page = 1) {
    $.ajax({
        url: '/orders/get_menus/',
        data: {hashtags: hashtags, page: page},
        dataType: 'json',
        success: function (data) {
            const menus = data.menus;
            const menuContainer = $('#menuContainer');
            menuContainer.empty();

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
            updatePaginationButtons(data.page_count, page);
        },
        error: function (error) {
            console.error('메뉴 업데이트 중 오류 발생:', error);
        }
    });
}

function updatePaginationButtons(totalPages, currentPage) {
    const paginationButtons = $('#paginationButtons');
    paginationButtons.empty();

    for (let i = 1; i <= totalPages; i++) {
        const button = `<button class="btn btn-outline-primary btn-page mr-1" onclick="changePage(${i})">${i}</button>`;
        paginationButtons.append(button);
    }
}

function changePage(pageNumber) {
    updateMenus("", pageNumber);
}
