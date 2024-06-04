let cart = {};

// // 장바구니 조회
// document.addEventListener('DOMContentLoaded', function() {
    
// });



        // cartData.forEach((menu, index) => {
        //     const cartItem = `
        //         <div class="recommendation" onclick="addItem('${menu.food_name}', ${menu.price}, '${menu.img_url}')">
        //             <h2>${menu.food_name}</h2>
        //             <div class="menu-image">
        //                 <img src="${menu.img_url}" alt="${menu.food_name} 이미지">
        //             </div>
        //             <p>${menu.price}원</p>
        //         </div>
        //     `;
        
        //     if (index === 0) {
        //         // Populating the popup with the first recommended menu
        //         popupImage.src = menu.img_url;
        //         popupName.textContent = menu.food_name;
        //         popupPrice.textContent = `${menu.price}원`;
        //         popupContainer.setAttribute('onclick', `addItem('${menu.food_name}', ${menu.price}, '${menu.img_url}')`);
        //         popupOverlay.style.display = 'flex';
        //     } else {
        //         // Inserting menu item into recommendations container
        //         recommendations.insertAdjacentHTML('beforeend', menuItem);
        //     }
        // });

        // closePopup.addEventListener("click", function(event) {
        //     event.stopPropagation(); // Stop event from bubbling up
        //     popupOverlay.style.display = "none"; // Hide the popup
        // });

        
    // 장바구니에 메뉴 추가
    function addItem(name, price, imgSrc) {
        // const username = 'mega'; // Replace with actual logic to get current username
        console.log("addItem name 들어오는지 >>>>>>", name) // 잘 찍히고 있음
        console.log("price 들어오는지 >>>>>", price) //
        console.log("imgSrc >>>>>", imgSrc) //
        console.log("params >>>>", { name: name, price:price, imgSrc: imgSrc })
        axios.post('/orders/add_to_cart/', { name: name, price:price, imgSrc: imgSrc})
            .then(response => {
                if (cart[name]) {
                    cart[name].count += 1;
                } else {
                    cart[name] = { price, count: 1, imgSrc };
                }
                updateCartDisplay();
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

    function updateCartDisplay(cartData) {
        const cartItems = cartData
        console.log("cartdata 넘어왔는지 >>>> ", cartData)
        let currentTotal = 0;
        console.log("cart가 뭐지 >>>>>", cart)
        for (let name in cart) {
            let item = cart[name];
            console.log("item 확인 >>> ", item)
            console.log("item을 메뉴 이름으로 value 부르기 >>>>", item["Iced Americano"])
            for (let menu in item) {
                const item_parsed = JSON.parse(item[menu])
                console.log("parse 됐는지 확인 >>>> ", item_parsed)
                currentTotal += item_parsed["price"] * item_parsed ["quantity"];
                console.log("menu의 가격이 잘 찍히는 지 >>>>>", item_parsed["price"])
                console.log("currentTotal >>>>", currentTotal)
                cartItems.innerHTML += `
                    <div class="cart-item">
                        <img src="${item.imgSrc}" alt="${name}">
                        <span>${name}</span>
                        <span>${item.price}원</span>
                        <span>${item.count}개</span>
                        <button class="remove" onclick="removeItem('${name}')">삭제</button>
                    </div>`;
            }
        }
    
        document.getElementById('totalPrice').textContent = `총 가격: ${currentTotal}원`;
        handleScrollArrows();
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

