
document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Обработчики для кнопок добавления/убавления
    document.querySelectorAll('.increase-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const productId = this.getAttribute('data-product-id');
            const productSlug = this.closest('.card').querySelector('.stretched-link').href.split('/').filter(Boolean).pop();
            addToCart(productId, productSlug, 1);
        });
    });

    document.querySelectorAll('.decrease-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const productId = this.getAttribute('data-product-id');
            const productSlug = this.closest('.card').querySelector('.stretched-link').href.split('/').filter(Boolean).pop();
            removeFromCart(productId, productSlug, 1);
        });
    });

    async function addToCart(productId, productSlug, quantity) {
        try {
            const response = await fetch(`/cart/api/cart/add/${productSlug}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    product: productId,
                    quantity: quantity
                })
            });

            if (response.ok) {
                const data = await response.json();

                // Обновление интерфейса
                const quantityElement = document.getElementById(`quantity-${productId}`);
                const currentQuantity = parseInt(quantityElement.textContent) || 0;
                quantityElement.textContent = currentQuantity + quantity;

                showFeedback('Товар добавлен в корзину', 'success');

                // Обновляем общее количество в корзине (если есть такой элемент)
                updateCartTotal();
            } else {
                const errorData = await response.json();
                showFeedback(`Ошибка: ${errorData.detail || 'Не удалось добавить товар'}`, 'danger');
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            showFeedback('Ошибка соединения с сервером', 'danger');
        }
    }

    async function removeFromCart(productId, productSlug, quantity) {
        try {
            // Сначала получаем текущее количество
            const quantityElement = document.getElementById(`quantity-${productId}`);
            let currentQuantity = parseInt(quantityElement.textContent) || 0;

            if (currentQuantity <= 0) {
                showFeedback('Товар отсутствует в корзине', 'warning');
                return;
            }

            // Для удаления можно использовать тот же endpoint с отрицательным количеством
            // или создать отдельный endpoint для уменьшения
            const response = await fetch(`/cart/api/cart/add/${productSlug}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    product: productId,
                    quantity: -quantity  // Отрицательное количество для уменьшения
                })
            });

            if (response.ok) {
                const data = await response.json();

                // Обновление интерфейса
                currentQuantity = Math.max(0, currentQuantity - quantity);
                quantityElement.textContent = currentQuantity;

                if (currentQuantity === 0) {
                    showFeedback('Товар удален из корзины', 'warning');
                } else {
                    showFeedback('Количество уменьшено', 'info');
                }

                // Обновляем общее количество в корзине
                updateCartTotal();
            } else {
                const errorData = await response.json();
                showFeedback(`Ошибка: ${errorData.detail || 'Не удалось обновить корзину'}`, 'danger');
            }
        } catch (error) {
            console.error('Error removing from cart:', error);
            showFeedback('Ошибка соединения с сервером', 'danger');
        }
    }

    function showFeedback(message, type) {
        // Создание временного уведомления
        const feedback = document.createElement('div');
        feedback.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        feedback.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        feedback.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(feedback);

        // Автоматическое скрытие через 3 секунды
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.remove();
            }
        }, 3000);
    }

    function updateCartTotal() {
        // Обновление счетчика корзины в шапке (если есть)
        const cartCounter = document.querySelector('.cart-counter');
        if (cartCounter) {
            // Можно сделать запрос к API для получения актуального количества
            fetch('/cart/api/cart/total/')
                .then(response => response.json())
                .then(data => {
                    cartCounter.textContent = data.total_quantity || 0;
                })
                .catch(error => console.error('Error updating cart total:', error));
        }
    }

    // Загрузка текущего состояния корзины при загрузке страницы
    async function loadCartState() {
        try {
            const response = await fetch('/cart/api/cart/');
            if (response.ok) {
                const cartData = await response.json();

                // Обновляем счетчики для каждого товара
                cartData.forEach(item => {
                    const quantityElement = document.getElementById(`quantity-${item.product}`);
                    if (quantityElement) {
                        quantityElement.textContent = item.quantity;
                    }
                });
            }
        } catch (error) {
            console.error('Error loading cart state:', error);
        }
    }

    // Инициализация при загрузке страницы
    loadCartState();
});

