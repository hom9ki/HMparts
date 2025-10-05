// product_card.js

let lastAction = null;
let lastProductSlug = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeProductCard();
    activateFirstButton();
});

function initializeProductCard() {
    const actionButtons = document.querySelectorAll('.action-btn');

    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const productSlug = getProductSlug();

            if (productSlug && action) {
                // Убираем активный класс у всех кнопок
                actionButtons.forEach(btn => {
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-outline-primary', 'btn-outline-success', 'btn-outline-info', 'btn-outline-warning', 'btn-outline-secondary');
                });

                // Добавляем активный класс к текущей кнопке
                const currentColor = this.classList.contains('btn-outline-primary') ? 'primary' :
                                   this.classList.contains('btn-outline-success') ? 'success' :
                                   this.classList.contains('btn-outline-info') ? 'info' :
                                   this.classList.contains('btn-outline-warning') ? 'warning' :
                                   this.classList.contains('btn-outline-secondary') ? 'secondary' : 'primary';

                this.classList.remove(`btn-outline-${currentColor}`);
                this.classList.add(`btn-${currentColor}`);

                loadContent(action, productSlug);
            } else {
                console.error('Product slug or action not found');
                showError(
                    document.getElementById('results-content'),
                    'Не удалось определить товар'
                );
            }
        });
    });

    const closeBtn = document.querySelector('#api-results .btn-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeResults);
    }

    const resultsContainer = document.getElementById('api-results');
    if (resultsContainer) {
        resultsContainer.addEventListener('show', function() {
            this.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
    }
}

function activateFirstButton() {
    const firstButton = document.querySelector('.action-btn');
    if (firstButton) {
        setTimeout(() => {
            firstButton.click();
        }, 100);
    }
}

function getProductSlug() {
    const productElement = document.querySelector('[data-product-slug]');
    if (productElement) {
        const slug = productElement.getAttribute('data-product-slug');
        console.log('Found product slug from data-attribute:', slug);
        return slug;
    }

    const hiddenInput = document.querySelector('input[name="product_slug"]');
    if (hiddenInput) {
        console.log('Found product slug from hidden input:', hiddenInput.value);
        return hiddenInput.value;
    }

    const path = window.location.pathname;
    const patterns = [
        /\/products\/([^\/]+)/,
        /\/product\/([^\/]+)/,
        /\/item\/([^\/]+)/,
        /\/goods\/([^\/]+)/,
        /\/catalog\/([^\/]+)/,
        /\/([^\/]+)\/$/
    ];

    for (const pattern of patterns) {
        const match = path.match(pattern);
        if (match) {
            const slug = match[1];
            console.log('Found product slug from URL:', slug);
            return slug;
        }
    }

    console.error('Could not find product slug');
    return null;
}

function loadContent(action, productSlug) {
    const resultsContainer = document.getElementById('api-results');
    const resultsTitle = document.getElementById('results-title');
    const resultsContent = document.getElementById('results-content');

    if (!resultsContainer || !resultsTitle || !resultsContent) {
        console.error('Required DOM elements not found');
        return;
    }

    lastAction = action;
    lastProductSlug = productSlug;

    showLoading(resultsContent);
    resultsContainer.style.display = 'block';
    setResultsTitle(resultsTitle, action);

    setTimeout(() => {
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);

    const csrftoken = getCookie('csrftoken');

    fetch(`/api/product/${productSlug}/${action}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || `Ошибка HTTP! Статус: ${response.status}`);
            }).catch(() => {
                throw new Error(`Ошибка HTTP! Статус: ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        displayContent(resultsContent, action, data);
    })
    .catch(error => {
        console.error('Error:', error);
        showError(resultsContent, error.message);
    });
}

function showLoading(container) {
    if (!container) return;

    container.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Загрузка...</span>
            </div>
            <p class="mt-3 text-muted">Загрузка данных...</p>
        </div>
    `;
}

function setResultsTitle(titleElement, action) {
    if (!titleElement) return;

    const titles = {
        'descriptions': '📝 Описание товара',
        'reviews': '⭐ Отзывы о товаре',
        'specifications': '⚙️ Характеристики товара',
        'questions': '❓ Вопросы и ответы',
        'set': '📦 В какие наборы входит этот товар'
    };

    titleElement.textContent = titles[action] || '📊 Результаты';
}

function displayContent(container, action, data) {
    if (!container) return;

    if (!data || data.length === 0) {
        // Если данных нет, но это отзывы - показываем форму
        if (action === 'reviews') {
            displayReviewFormOnly(container);
            return;
        }

        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                <p class="text-muted">Данные не найдены</p>
            </div>
        `;
        return;
    }

    switch (action) {
        case 'descriptions':
            displayDescriptions(container, data);
            break;
        case 'reviews':
            displayReviews(container, data);
            break;
        case 'specifications':
            displaySpecifications(container, data);
            break;
        case 'questions':
            displayQuestions(container, data);
            break;
        case 'set':
            displaySet(container, data);
            break;
        default:
            container.innerHTML = '<p class="text-muted">Неизвестный тип данных</p>';
    }
}

function displayDescriptions(container, data) {
    let html = '<div class="descriptions-content">';

    data.forEach((desc, index) => {
        const icon = getDescriptionIcon(desc.description_type);

        html += `
            <div class="description-item ${index !== data.length - 1 ? 'border-bottom pb-4 mb-4' : ''}">
                ${desc.description_type ? `
                    <div class="d-flex align-items-center mb-3">
                        <div class="description-icon bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                            <i class="${icon}"></i>
                        </div>
                        <h6 class="fw-bold text-primary mb-0">${desc.description_type}</h6>
                    </div>
                ` : ''}

                ${desc.content ? `
                    <div class="description-text bg-light p-3 rounded mb-3">
                        ${formatText(desc.content)}
                    </div>
                ` : ''}

                ${desc.created_at ? `
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="far fa-calendar me-1"></i>
                            ${new Date(desc.created_at).toLocaleDateString('ru-RU')}
                        </small>
                        ${desc.order ? `<small class="text-muted">Порядок: ${desc.order}</small>` : ''}
                    </div>
                ` : ''}
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

function getDescriptionIcon(descriptionType) {
    if (!descriptionType) return 'fas fa-file-alt';

    const type = descriptionType.toLowerCase();

    if (type.includes('технич') || type.includes('характеристик')) {
        return 'fas fa-cogs';
    } else if (type.includes('преимуществ') || type.includes('плюс')) {
        return 'fas fa-star';
    } else if (type.includes('инструкц') || type.includes('использован')) {
        return 'fas fa-book';
    } else if (type.includes('гарант') || type.includes('обслуживан')) {
        return 'fas fa-shield-alt';
    } else if (type.includes('доставк') || type.includes('установк')) {
        return 'fas fa-truck';
    } else if (type.includes('отзыв') || type.includes('рекомендац')) {
        return 'fas fa-comment';
    } else {
        return 'fas fa-file-alt';
    }
}

function displayReviews(container, data) {
    const productSlug = getProductSlug();

    let html = `
        <div class="reviews-section">
            <!-- Форма добавления отзыва -->
            <div class="review-form-card mb-5">
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-edit me-2"></i>
                            Оставить отзыв
                        </h5>
                    </div>
                    <div class="card-body">
                        <form id="add-review-form">
                            <div class="mb-3">
                                <label for="review-rating" class="form-label">Оценка</label>
                                <div class="rating-stars mb-2">
                                    ${generateRatingStars()}
                                </div>
                                <input type="hidden" id="review-rating" name="rating" required>
                            </div>
                            <div class="mb-3">
                                <label for="review-text" class="form-label">Текст отзыва</label>
                                <textarea class="form-control" id="review-text" name="text"
                                          rows="4" placeholder="Поделитесь вашим мнением о товаре..."
                                          required></textarea>
                            </div>
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">
                                    <i class="fas fa-info-circle me-1"></i>
                                    Ваш отзыв будет опубликован после проверки
                                </small>
                                <button type="submit" class="btn btn-primary" id="submit-review-btn">
                                    <i class="fas fa-paper-plane me-2"></i>
                                    Отправить отзыв
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Список отзывов -->
            <div class="reviews-list">
                <h5 class="mb-4">
                    <i class="fas fa-comments me-2"></i>
                    Отзывы покупателей (${data.length})
                </h5>
    `;

    if (data.length === 0) {
        html += `
            <div class="text-center py-5">
                <i class="fas fa-comments fa-3x text-muted mb-3"></i>
                <p class="text-muted fs-5">Пока нет отзывов</p>
                <p class="text-muted">Будьте первым, кто оставит отзыв об этом товаре!</p>
            </div>
        `;
    } else {
        data.forEach((review, index) => {
            const reviewDate = review.created_at ? new Date(review.created_at).toLocaleDateString('ru-RU') : '';
            const userName = review.user_name || 'Анонимный пользователь';
            const userAvatar = review.avatar || '/static/images/default-avatar.png';
            const initials = getUserInitials(userName);
            console.log(userName, userAvatar, review.avatar, review.rating);

            html += `
                <div class="review-item card mb-4 border-0 shadow-sm animate__animated animate__fadeInUp"
                     style="animation-delay: ${index * 0.1}s;">
                    <div class="card-body">
                        <div class="review-header d-flex justify-content-between align-items-start mb-3">
                            <div class="user-info d-flex align-items-center">
                                <div class="user-avatar-wrapper position-relative me-3">
                                    <img src="${userAvatar}"
                                         alt="${userName}"
                                         class="user-avatar rounded-circle"
                                         style="width: 50px; height: 50px; object-fit: cover;"
                                         onerror="this.src='${generateAvatarSVG(initials, index)}'">
                                </div>
                                <div class="user-details">
                                    <h6 class="mb-1 fw-bold text-dark">${userName}</h6>
                                    <div class="rating-small text-warning">
                                        ${generateStarRating(review.get_avg_rating)}
                                    </div>
                                </div>
                            </div>
                            <div class="review-meta text-end">
                                <small class="text-muted">
                                    <i class="far fa-calendar me-1"></i>
                                    ${reviewDate}
                                </small>
                            </div>
                        </div>

                        <div class="review-content">
                            <div class="review-text bg-light p-3 rounded position-relative">
                                <div class="quote-icon text-primary opacity-25 position-absolute top-0 start-0 mt-2 ms-2">
                                    <i class="fas fa-quote-left fa-lg"></i>
                                </div>
                                <p class="mb-0 lh-lg ps-4">${formatText(review.text)}</p>
                                <div class="quote-icon text-primary opacity-25 position-absolute bottom-0 end-0 mb-2 me-2">
                                    <i class="fas fa-quote-right fa-lg"></i>
                                </div>
                            </div>
                        </div>

                        ${review.advantages || review.disadvantages ? `
                            <div class="review-pros-cons mt-3 row">
                                ${review.advantages ? `
                                    <div class="col-md-6">
                                        <div class="pros text-success">
                                            <small class="fw-bold">
                                                <i class="fas fa-thumbs-up me-1"></i>
                                                Достоинства:
                                            </small>
                                            <p class="mb-0 small">${formatText(review.advantages)}</p>
                                        </div>
                                    </div>
                                ` : ''}
                                ${review.disadvantages ? `
                                    <div class="col-md-6">
                                        <div class="cons text-danger">
                                            <small class="fw-bold">
                                                <i class="fas fa-thumbs-down me-1"></i>
                                                Недостатки:
                                            </small>
                                            <p class="mb-0 small">${formatText(review.disadvantages)}</p>
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        });
    }

    html += `
            </div>
        </div>
    `;

    container.innerHTML = html;

    // Инициализируем обработчики для формы
    initializeReviewForm(productSlug);

    // Добавляем анимацию при скролле
    animateReviewsOnScroll();
}

function displayReviewFormOnly(container) {
    const productSlug = getProductSlug();

    let html = `
        <div class="reviews-section">
            <!-- Форма добавления отзыва -->
            <div class="review-form-card">
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-edit me-2"></i>
                            Оставить отзыв о товаре
                        </h5>
                    </div>
                    <div class="card-body">
                        <form id="add-review-form">
                            <div class="mb-3">
                                <label for="review-rating" class="form-label">Ваша оценка</label>
                                <div class="rating-stars mb-2">
                                    ${generateRatingStars()}
                                </div>
                                <input type="hidden" id="review-rating" name="rating" required>
                                <small class="text-muted">Выберите от 1 до 5 звезд</small>
                            </div>
                            <div class="mb-3">
                                <label for="review-text" class="form-label">Текст отзыва</label>
                                <textarea class="form-control" id="review-text" name="text"
                                          rows="5" placeholder="Расскажите о вашем опыте использования товара. Что вам понравилось? Что можно улучшить?"
                                          required></textarea>
                            </div>
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">
                                    <i class="fas fa-info-circle me-1"></i>
                                    Ваш отзыв будет опубликован после проверки модератором
                                </small>
                                <button type="submit" class="btn btn-primary" id="submit-review-btn">
                                    <i class="fas fa-paper-plane me-2"></i>
                                    Опубликовать отзыв
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Сообщение о том, что отзывов пока нет -->
            <div class="text-center mt-4">
                <i class="fas fa-comments fa-3x text-muted mb-3"></i>
                <p class="text-muted">Пока нет отзывов о этом товаре. Будьте первым!</p>
            </div>
        </div>
    `;

    container.innerHTML = html;

    // Инициализируем обработчики для формы
    initializeReviewForm(productSlug);
}

// НОВАЯ ФУНКЦИЯ: Отображение вопросов и ответов
function displayQuestions(container, data) {
    let html = '<div class="questions-content">';

    // Добавляем форму для вопроса
    html += `
        <div class="question-form-card mb-5">
            <div class="card border-info">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0">
                        <i class="fas fa-question-circle me-2"></i>
                        Задать вопрос о товаре
                    </h5>
                </div>
                <div class="card-body">
                    <form id="add-question-form">
                        <div class="mb-3">
                            <label for="question-text" class="form-label">Ваш вопрос</label>
                            <textarea class="form-control" id="question-text" name="text"
                                      rows="3" placeholder="Задайте вопрос о товаре..."
                                      required></textarea>
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-info-circle me-1"></i>
                                Ваш вопрос будет опубликован после проверки
                            </small>
                            <button type="submit" class="btn btn-info" id="submit-question-btn">
                                <i class="fas fa-paper-plane me-2"></i>
                                Задать вопрос
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <h5 class="mb-4">
            <i class="fas fa-comments me-2"></i>
            Вопросы и ответы (${data.length})
        </h5>
    `;

    if (data.length === 0) {
        html += `
            <div class="text-center py-5">
                <i class="fas fa-question-circle fa-3x text-muted mb-3"></i>
                <p class="text-muted fs-5">Пока нет вопросов</p>
                <p class="text-muted">Будьте первым, кто задаст вопрос об этом товаре!</p>
            </div>
        `;
    } else {
        data.forEach((qa, index) => {
            const questionDate = qa.created_at ? new Date(qa.created_at).toLocaleDateString('ru-RU') : '';
            const userName = qa.user_name || 'Анонимный пользователь';

            html += `
                <div class="qa-item card mb-4 border-0 shadow-sm animate__animated animate__fadeInUp"
                     style="animation-delay: ${index * 0.1}s;">
                    <div class="card-body">
                        <!-- Вопрос -->
                        <div class="question mb-4">
                            <div class="d-flex align-items-start mb-3">
                                <div class="question-icon bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                                     style="width: 40px; height: 40px;">
                                    <i class="fas fa-question"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <div class="d-flex justify-content-between align-items-start">
                                        <div>
                                            <strong class="d-block text-dark">${userName}</strong>
                                            <small class="text-muted">
                                                <i class="far fa-calendar me-1"></i>
                                                ${questionDate}
                                            </small>
                                        </div>
                                        <span class="badge ${qa.is_answered ? 'bg-success' : 'bg-warning'}">
                                            ${qa.is_answered ? '✓ Отвечено' : '⏳ Ожидает ответа'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div class="question-text bg-light p-3 rounded position-relative">
                                <div class="quote-icon text-primary opacity-25 position-absolute top-0 start-0 mt-2 ms-2">
                                    <i class="fas fa-quote-left"></i>
                                </div>
                                <p class="mb-0 lh-lg ps-4">${formatText(qa.text)}</p>
                            </div>
                        </div>

                        <!-- Ответы -->
                        ${qa.answers && qa.answers.length > 0 ? `
                            <div class="answers-section">
                                <h6 class="text-success mb-3">
                                    <i class="fas fa-reply me-2"></i>
                                    Ответы (${qa.answers.length})
                                </h6>
                                ${qa.answers.map((answer, answerIndex) => {
                                    const answerDate = answer.created_at ? new Date(answer.created_at).toLocaleDateString('ru-RU') : '';
                                    const answerUserName = answer.user_name || 'Продавец';

                                    return `
                                        <div class="answer-item mb-3 ${answerIndex !== qa.answers.length - 1 ? 'border-bottom pb-3' : ''}">
                                            <div class="d-flex align-items-start mb-2">
                                                <div class="answer-icon bg-success text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                                                     style="width: 35px; height: 35px;">
                                                    <i class="fas fa-check"></i>
                                                </div>
                                                <div class="flex-grow-1">
                                                    <strong class="d-block text-success">${answerUserName}</strong>
                                                    <small class="text-muted">
                                                        <i class="far fa-calendar me-1"></i>
                                                        ${answerDate}
                                                    </small>
                                                </div>
                                            </div>
                                            <div class="answer-text bg-success bg-opacity-10 p-3 rounded position-relative ms-5">
                                                <div class="quote-icon text-success opacity-25 position-absolute top-0 start-0 mt-1 ms-2">
                                                    <i class="fas fa-quote-left"></i>
                                                </div>
                                                <p class="mb-0 lh-base ps-3">${formatText(answer.text)}</p>
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        ` : qa.is_answered ? `
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                Ответ готовится и скоро будет опубликован
                            </div>
                        ` : `
                            <div class="alert alert-warning">
                                <i class="fas fa-clock me-2"></i>
                                Ожидает ответа от продавца
                            </div>
                        `}
                    </div>
                </div>
            `;
        });
    }

    html += '</div>';
    container.innerHTML = html;

    // Инициализируем обработчики для формы вопроса
    initializeQuestionForm();

    // Добавляем анимацию при скролле
    animateQuestionsOnScroll();
}

// НОВАЯ ФУНКЦИЯ: Инициализация формы вопроса
function initializeQuestionForm() {
    const form = document.getElementById('add-question-form');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const submitBtn = document.getElementById('submit-question-btn');
        const originalText = submitBtn.innerHTML;
        const productSlug = getProductSlug();

        // Блокируем кнопку
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Отправка...';

        const formData = new FormData(this);
        const questionData = {
            text: formData.get('text')
        };

        try {
            const response = await fetch(`/api/product/${productSlug}/add-question/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(questionData)
            });

            if (!response.ok) {
                const errorText = await response.text();
                let errorData;
                try {
                    errorData = JSON.parse(errorText);
                } catch {
                    errorData = { error: errorText };
                }
                throw new Error(errorData.error || 'Ошибка при отправке вопроса');
            }

            const newQuestion = await response.json();

            // Показываем уведомление об успехе
            showNotification('Вопрос успешно отправлен!', 'success');

            // Очищаем форму
            form.reset();

            // Перезагружаем вопросы
            if (lastAction === 'questions' && lastProductSlug) {
                loadContent('questions', lastProductSlug);
            }

        } catch (error) {
            console.error('Ошибка при отправке вопроса:', error);
            showNotification(error.message || 'Ошибка при отправке вопроса', 'error');
        } finally {
            // Разблокируем кнопку
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

// НОВАЯ ФУНКЦИЯ: Анимация вопросов при скролле
function animateQuestionsOnScroll() {
    const qaItems = document.querySelectorAll('.qa-item');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });

    qaItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        item.style.transition = 'all 0.6s ease';
        observer.observe(item);
    });
}

function generateAvatarSVG(initials, index) {
    const colors = ['#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8'];
    const color = colors[index % colors.length];
    const safeInitials = (initials || 'UU').substring(0, 2).toUpperCase();

    const svg = `<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
        <rect width="50" height="50" fill="${color}" rx="25"/>
        <text x="25" y="32" text-anchor="middle" fill="white" font-family="Arial" font-size="16" font-weight="bold">${safeInitials}</text>
    </svg>`;

    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

function getUserInitials(username) {
    if (!username) return 'UU';
    const parts = username.split(' ').filter(part => part.length > 0);
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return username.substring(0, 2).toUpperCase();
}

function generateRatingStars() {
    let html = '<div class="d-flex gap-1">';
    for (let i = 1; i <= 5; i++) {
        html += `
            <i class="fas fa-star rating-star" data-rating="${i}"
               style="cursor: pointer; font-size: 1.5rem; color: #ddd;"
               onmouseover="highlightStars(${i})"
               onmouseout="resetStars()"
               onclick="setRating(${i})"></i>
        `;
    }
    html += '</div>';
    return html;
}

function highlightStars(rating) {
    const stars = document.querySelectorAll('.rating-star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.style.color = '#ffc107';
        } else {
            star.style.color = '#ddd';
        }
    });
}

function resetStars() {
    const currentRating = document.getElementById('review-rating').value || 0;
    const stars = document.querySelectorAll('.rating-star');
    stars.forEach((star, index) => {
        if (index < currentRating) {
            star.style.color = '#ffc107';
        } else {
            star.style.color = '#ddd';
        }
    });
}

function setRating(rating) {
    document.getElementById('review-rating').value = rating;
    const stars = document.querySelectorAll('.rating-star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.style.color = '#ffc107';
        } else {
            star.style.color = '#ddd';
        }
    });
}

function initializeReviewForm(productSlug) {
    const form = document.getElementById('add-review-form');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const submitBtn = document.getElementById('submit-review-btn');
        const originalText = submitBtn.innerHTML;

        // Блокируем кнопку
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Отправка...';

        const formData = new FormData(this);
        const reviewData = {
            text: formData.get('text'),
            rating: parseInt(formData.get('rating'))
        };
        console.log('Review data:', reviewData);
        try {
            const response = await fetch(`/feedback/api/review/${productSlug}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(reviewData)
            });
            console.log('Response:', response);

            if (!response.ok) {
                // Исправленная обработка ошибок - читаем тело ответа только один раз
                const errorText = await response.text();
                console.error('❌ Текст ошибки:', errorText);

                let errorData;
                try {
                    errorData = JSON.parse(errorText);
                } catch {
                    errorData = { error: errorText };
                }

                throw new Error(errorData.error || 'Ошибка при отправке отзыва');
            }

            const newReview = await response.json();

            // Показываем уведомление об успехе
            showNotification('Отзыв успешно отправлен!', 'success');

            // Очищаем форму
            form.reset();
            document.getElementById('review-rating').value = '';
            resetStars();

            // Перезагружаем отзывы
            if (lastAction === 'reviews' && lastProductSlug) {
                loadContent('reviews', lastProductSlug);
            }

        } catch (error) {
            console.error('Ошибка при отправке отзыва:', error);
            showNotification(error.message || 'Ошибка при отправке отзыва', 'error');
        } finally {
            // Разблокируем кнопку
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

function showNotification(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' :
                      type === 'error' ? 'alert-danger' : 'alert-info';

    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
    `;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Автоматически скрываем через 5 секунд
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function animateReviewsOnScroll() {
    const reviewItems = document.querySelectorAll('.review-item');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });

    reviewItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        item.style.transition = 'all 0.6s ease';
        observer.observe(item);
    });
}

function displaySpecifications(container, data) {
    let html = '<div class="specifications-content">';

    // Группируем характеристики по группам
    const groups = {};
    data.forEach(spec => {
        const group = spec.group || 'Основные';
        if (!groups[group]) {
            groups[group] = [];
        }
        groups[group].push(spec);
    });

    Object.keys(groups).forEach((groupName, groupIndex) => {
        html += `
            <div class="spec-group ${groupIndex !== 0 ? 'mt-4' : ''}">
                <h6 class="fw-bold text-primary mb-3">${groupName}</h6>
                <div class="specifications-table">
        `;

        groups[groupName].forEach((spec, index) => {
            html += `
                <div class="row py-2 ${index % 2 === 0 ? 'bg-light' : ''}">
                    <div class="col-6 fw-bold">${spec.name || ''}</div>
                    <div class="col-6">${spec.value || '—'}</div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

function generateStarRating(rating) {
    console.log(rating);
    if (!rating || rating === 0) {
        return '<span class="text-muted small">Нет оценки</span>';
    }

    let stars = '';
    for (let i = 1; i <= 5; i++) {
        if (i <= rating) {
            stars += '<i class="fas fa-star"></i>';
        } else {
            stars += '<i class="far fa-star"></i>';
        }
    }
    return stars;
}

function formatText(text) {
    if (!text) return '';
    return text.replace(/\n/g, '<br>');
}

function showError(container, message) {
    if (!container) return;

    container.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <div class="d-flex align-items-center">
                <i class="fas fa-exclamation-triangle me-3 fs-4"></i>
                <div class="flex-grow-1">
                    <h6 class="alert-heading mb-1">Ошибка загрузки данных</h6>
                    <p class="mb-0">${message || 'Произошла неизвестная ошибка'}</p>
                </div>
            </div>
            ${lastAction && lastProductSlug ? `
                <div class="mt-3">
                    <button class="btn btn-sm btn-outline-danger" onclick="retryLastAction()">
                        <i class="fas fa-redo me-1"></i>Попробовать снова
                    </button>
                </div>
            ` : ''}
        </div>
    `;
}

function retryLastAction() {
    if (lastAction && lastProductSlug) {
        loadContent(lastAction, lastProductSlug);
    }
}

function closeResults() {
    const resultsContainer = document.getElementById('api-results');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функция для открытия модального окна с изображением
function openImageModal(imageUrl, imageAlt = '') {
    const modalImage = document.getElementById('modalImage');
    const imageModal = document.getElementById('imageModal');

    if (!modalImage || !imageModal) {
        console.error('Modal elements not found');
        return;
    }

    // Устанавливаем изображение
    modalImage.src = imageUrl;
    modalImage.alt = imageAlt;

    // Показываем модальное окно
    const modal = new bootstrap.Modal(imageModal);
    modal.show();

    // Добавляем красивую анимацию появления
    modalImage.style.opacity = '0';
    setTimeout(() => {
        modalImage.style.transition = 'opacity 0.3s ease';
        modalImage.style.opacity = '1';
    }, 100);
}

// Функция для добавления обработчиков на все изображения
function initializeImageModals() {
    // Обработчик для всех изображений с классом modal-image
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-image')) {
            e.preventDefault();
            openImageModal(e.target.src, e.target.alt);
        }
    });

    // Добавляем стили для интерактивности
    const modalImages = document.querySelectorAll('.modal-image');
    modalImages.forEach(img => {
        img.style.transition = 'transform 0.2s ease, box-shadow 0.2s ease';

        // Эффект при наведении
        img.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
            if (this.classList.contains('main-product-image')) {
                this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
            }
        });

        img.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = 'none';
        });
    });
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    initializeImageModals();

    // Также можно добавить обработчик для клавиши ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = bootstrap.Modal.getInstance(document.getElementById('imageModal'));
            if (modal) {
                modal.hide();
            }
        }
    });
});

// Глобальные функции для звезд рейтинга
window.openImageModal = openImageModal;
window.highlightStars = highlightStars;
window.resetStars = resetStars;
window.setRating = setRating;

function displaySet(container, data) {
    let totalPrice = 0;

    let html = `
        <div class="set-content">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-light">
                        <tr>
                            <th width="60">Кол-во</th>
                            <th>Наименование</th>
                            <th width="120" class="text-end">Цена</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    data.forEach(item => {
        console.log(item.total_price);
        const quantity = item.quantity || 1;
        const price = item.total_price || 0;
        totalPrice += price * quantity;

        html += `
            <tr>
                <td>
                    <span class="badge bg-primary fs-6">${quantity}</span>
                </td>
                <td>
                    <div>
                        <strong class="d-block">${item.name || 'Неизвестный элемент'}</strong>
                        ${item.description ? `<small class="text-muted">${item.description}</small>` : ''}
                        ${item.sku ? `<div><small class="text-muted">Артикул: ${item.sku}</small></div>` : ''}
                    </div>
                </td>
                <td class="text-end">
                    ${price > 0 ? `<span class="fw-bold text-primary">${price} ₽</span>` : '<span class="text-muted">—</span>'}
                </td>
            </tr>
        `;
    });

    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}