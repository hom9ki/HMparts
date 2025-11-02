// cart.js - финальная версия для страницы корзины
document.addEventListener('DOMContentLoaded', function() {
    initializeCart();
});

function getCSRFToken() {
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfTokenElement) {
        return csrfTokenElement.value;
    }

    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];

    return cookieValue || '';
}

function initializeCart() {
    initializeCartPageEventListeners();
    loadCartState();
}

function initializeCartPageEventListeners() {
    document.querySelectorAll('.cart-item').forEach(cartItem => {
        const plusBtn = cartItem.querySelector('.increase-btn');
        const minusBtn = cartItem.querySelector('.decrease-btn');
        const quantityInput = cartItem.querySelector('.quantity-input');
        const deleteLink = cartItem.querySelector('.delete-btn');
        const productSlug = cartItem.getAttribute('data-product-slug');
        const productId = cartItem.getAttribute('data-product-id');

        if (!productSlug) {
            console.warn('Product slug not found for cart item');
            return;
        }

        // Обработчик кнопки +
        if (plusBtn) {
            plusBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const totalPriceElement = cartItem.querySelector('.item-total-price');
                const unitPriceElement = cartItem.querySelector('.item-unit-price');
                const currentQuantity = parseInt(quantityInput?.value) || 0;
                const maxQuantity = parseInt(quantityInput?.getAttribute('max')) || 999;

                if (currentQuantity >= maxQuantity) {
                    showFeedback(`Максимальное количество: ${maxQuantity} шт.`, 'warning');
                    return;
                }

                updateCartItem(productId, productSlug, 1, quantityInput, totalPriceElement, unitPriceElement);
            });
        }

        // Обработчик кнопки -
        if (minusBtn) {
            minusBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const totalPriceElement = cartItem.querySelector('.item-total-price');
                const unitPriceElement = cartItem.querySelector('.item-unit-price');
                const currentQuantity = parseInt(quantityInput?.value) || 0;

                if (currentQuantity <= 1) {
                    if (confirm('Удалить товар из корзины?')) {
                        removeCartItem(productId, productSlug, cartItem);
                    }
                } else {
                    updateCartItem(productId, productSlug, -1, quantityInput, totalPriceElement, unitPriceElement);
                }
            });
        }

        // Обработчик изменения поля ввода
        if (quantityInput) {
            quantityInput.addEventListener('change', function(e) {
                const newQuantity = parseInt(this.value) || 1;
                const currentQuantity = parseInt(this.getAttribute('data-current-quantity')) || 1;
                const maxQuantity = parseInt(this.getAttribute('max')) || 999;
                const minQuantity = parseInt(this.getAttribute('min')) || 1;

                // Проверяем границы
                if (newQuantity > maxQuantity) {
                    showFeedback(`Максимальное количество: ${maxQuantity} шт.`, 'warning');
                    this.value = maxQuantity;
                    return;
                }

                if (newQuantity < minQuantity) {
                    showFeedback(`Минимальное количество: ${minQuantity} шт.`, 'warning');
                    this.value = minQuantity;
                    return;
                }

                const difference = newQuantity - currentQuantity;
                const totalPriceElement = cartItem.querySelector('.item-total-price');
                const unitPriceElement = cartItem.querySelector('.item-unit-price');

                if (difference !== 0) {
                    updateCartItem(productId, productSlug, difference, quantityInput, totalPriceElement, unitPriceElement);
                }
            });

            quantityInput.setAttribute('data-current-quantity', quantityInput.value);
        }

        // Обработчик удаления товара
        if (deleteLink) {
            deleteLink.addEventListener('click', function(e) {
                e.preventDefault();
                if (confirm('Вы уверены, что хотите удалить товар из корзины?')) {
                    removeCartItem(productId, productSlug, cartItem);
                }
            });
        }
    });
}

async function updateCartItem(productId, productSlug, quantity, quantityInput, totalPriceElement, unitPriceElement) {
    const csrfToken = getCSRFToken();

    try {
        // Получаем текущее значение и максимальное количество
        const currentQuantity = parseInt(quantityInput.value) || 0;
        const maxQuantity = parseInt(quantityInput.getAttribute('max')) || 999;
        const newQuantity = currentQuantity + quantity;

        // Проверяем не превышает ли новое количество максимальное
        if (newQuantity > maxQuantity) {
            showFeedback(`Максимальное количество: ${maxQuantity} шт.`, 'warning');
            return;
        }

        // Проверяем чтобы количество было не меньше 1
        if (newQuantity < 1) {
            showFeedback('Минимальное количество: 1 шт.', 'warning');
            return;
        }

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

            // Проверяем ответ от сервера - не превышено ли количество
            if (data.quantity > maxQuantity) {
                showFeedback(`Максимальное количество: ${maxQuantity} шт.`, 'warning');
                quantityInput.value = maxQuantity;
                quantityInput.setAttribute('data-current-quantity', maxQuantity);
                return;
            }

            // Обновляем поле ввода количества
            if (quantityInput) {
                quantityInput.value = data.quantity;
                quantityInput.setAttribute('data-current-quantity', data.quantity);
            }

            // Обновляем цены
            if (totalPriceElement) {
                if (data.total_price !== undefined) {
                    totalPriceElement.textContent = `${parseFloat(data.total_price).toFixed(2)} ₽`;
                } else if (data.product_price !== undefined && data.quantity !== undefined) {
                    // Если total_price нет, вычисляем вручную
                    const calculatedTotal = data.product_price * data.quantity;
                    totalPriceElement.textContent = `${calculatedTotal.toFixed(2)} ₽`;
                }
            }

            if (unitPriceElement && data.product_price !== undefined) {
                unitPriceElement.textContent = `${parseFloat(data.product_price).toFixed(2)} ₽/шт`;
            }

            // Обновляем общие итоги
            updateCartTotals();

            showFeedback('Корзина обновлена', 'success');
        } else {
            const errorData = await response.json();
            showFeedback(`Ошибка: ${errorData.detail || errorData.error || 'Не удалось обновить корзину'}`, 'danger');
            // Возвращаем предыдущее значение
            if (quantityInput) {
                quantityInput.value = quantityInput.getAttribute('data-current-quantity');
            }
        }
    } catch (error) {
        console.error('Error updating cart item:', error);
        showFeedback('Ошибка соединения с сервером', 'danger');
        if (quantityInput) {
            quantityInput.value = quantityInput.getAttribute('data-current-quantity');
        }
    }
}

async function removeCartItem(productId, productSlug, cartItem) {
    const csrfToken = getCSRFToken();

    try {
        const response = await fetch(`/cart/api/cart/remove/${productSlug}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            }
        });

        if (response.ok || response.status === 204) {
            // Анимация удаления
            cartItem.style.opacity = '0';
            cartItem.style.transform = 'translateX(100px)';
            cartItem.style.transition = 'all 0.3s ease';

            setTimeout(() => {
                cartItem.remove();
                updateCartTotals();

                // Проверяем, остались ли товары в корзине
                const remainingItems = document.querySelectorAll('.cart-item');
                if (remainingItems.length === 0) {
                    showEmptyCartMessage();
                }
            }, 300);

            showFeedback('Товар удален из корзины', 'warning');
        } else {
            let errorMessage = 'Не удалось удалить товар';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorData.detail || errorMessage;
            } catch (e) {
                errorMessage = `Ошибка ${response.status}`;
            }
            showFeedback(`Ошибка: ${errorMessage}`, 'danger');
        }
    } catch (error) {
        console.error('Error removing from cart:', error);
        showFeedback('Ошибка соединения с сервером', 'danger');
    }
}

async function updateCartTotal() {
    const cartCounter = document.querySelector('.cart-counter');
    if (cartCounter) {
        try {
            const response = await fetch('/cart/api/cart/');
            if (response.ok) {
                const cartData = await response.json();
                const totalQuantity = cartData.reduce((sum, item) => sum + item.quantity, 0);
                cartCounter.textContent = totalQuantity;
            }
        } catch (error) {
            console.error('Error updating cart total:', error);
        }
    }
}

async function updateCartTotals() {
    try {
        const response = await fetch('/cart/api/cart/');
        if (response.ok) {
            const cartData = await response.json();

            // Пересчитываем общие суммы
            let totalQuantity = 0;
            let totalPrice = 0;

            cartData.forEach(item => {
                totalQuantity += item.quantity;

                if (item.total_price !== undefined) {
                    totalPrice += parseFloat(item.total_price);
                } else if (item.product_price !== undefined && item.quantity !== undefined) {
                    totalPrice += parseFloat(item.product_price) * item.quantity;
                }
            });

            // Обновляем элементы на странице корзины
            const totalQuantityElements = document.querySelectorAll('.total-quantity');
            const totalPriceElements = document.querySelectorAll('.total-price');

            totalQuantityElements.forEach(element => {
                element.textContent = totalQuantity;
            });

            totalPriceElements.forEach(element => {
                element.textContent = `${totalPrice.toFixed(2)} ₽`;
            });

            // Обновляем счетчик в шапке
            updateCartTotal();
        }
    } catch (error) {
        console.error('Error updating totals:', error);
    }
}

function showEmptyCartMessage() {
    setTimeout(() => {
        const cartContainer = document.querySelector('.card.shadow-sm.mb-4');
        if (cartContainer) {
            cartContainer.innerHTML = `
                <div class="card-body text-center py-5">
                    <i class="fas fa-shopping-cart fa-3x text-muted mb-3"></i>
                    <h3>Корзина пуста</h3>
                    <p class="text-muted">Добавьте товары, чтобы сделать заказ</p>
                    <a href="/" class="btn btn-primary">Перейти к покупкам</a>
                </div>
            `;
        }
    }, 500);
}

function showFeedback(message, type) {
    // Удаляем существующие уведомления
    document.querySelectorAll('.cart-feedback-alert').forEach(alert => {
        alert.remove();
    });

    // Создание временного уведомления
    const feedback = document.createElement('div');
    feedback.className = `alert alert-${type} alert-dismissible fade show position-fixed cart-feedback-alert`;
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

async function loadCartState() {
    try {
        const response = await fetch('/cart/api/cart/');
        if (response.ok) {
            const cartData = await response.json();

            // Обновляем счетчики на страницах каталога
            cartData.forEach(item => {
                const quantityElement = document.getElementById(`quantity-${item.product_id || item.product}`);
                if (quantityElement) {
                    quantityElement.textContent = item.quantity;
                }
            });

            // Обновляем общий счетчик
            updateCartTotal();
        }
    } catch (error) {
        console.error('Error loading cart state:', error);
    }
}

// Экспортируем функции для использования в других скриптах
window.CartManager = {
    updateCartItem,
    removeCartItem,
    updateCartTotal,
    updateCartTotals
};