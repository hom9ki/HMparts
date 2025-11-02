// Обработчик для кнопок API запросов
document.addEventListener('DOMContentLoaded', function() {
    const actionButtons = document.querySelectorAll('.action-btn');
    const resultsContainer = document.getElementById('api-results');
    const resultsTitle = document.getElementById('results-title');
    const resultsContent = document.getElementById('results-content');

    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const slug = this.getAttribute('data-slug');
            console.log(`Запрос на ${action} для ${slug}`);

            // Показываем индикатор загрузки
            resultsContent.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Загрузка...</p></div>';
            resultsContainer.style.display = 'block';

            // Выполняем API запрос
            fetch(`/api/set/${slug}/${action}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Обновляем заголовок
                    const titles = {
                        'descriptions': 'Описание комплекта',
                        'reviews': 'Отзывы о комплекте',
                        'questions': 'Вопросы о комплекте',
                        'set': 'Товары в комплекте'
                    };
                    resultsTitle.textContent = titles[action] || 'Результаты';

                    // Обрабатываем данные в зависимости от действия
                    displayResults(action, data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    resultsContent.innerHTML = '<div class="alert alert-danger">Ошибка при загрузке данных</div>';
                });
        });
    });

    function displayResults(action, data) {
        let html = '';

        switch(action) {
            case 'descriptions':
                // Для описания - просто выводим текст
                html = `<div class="set-description">
                           <p>${data.description || 'Описание отсутствует'}</p>
                        </div>`;
                break;

            case 'reviews':
            console.log('Reviews data:', data);
                // Для отзывов - выводим список
                if (data.length === 0) {
                    html = '<p class="text-muted">Отзывов пока нет</p>';
                } else {
                    html = '<div class="reviews-list">';
                    data.forEach(review => {
                    console.log('Review fields:', Object.keys(review));
                        html += `
                        <div class="review-item border-bottom pb-3 mb-3">
                            <div class="d-flex align-items-center mb-2">

                                <div>
                                    <strong>${review.user_name}</strong>
                                    <div class="text-warning">
                                        ${'★'.repeat(review.rating || 0)}${'☆'.repeat(5 - (review.rating || 0))}
                                    </div>
                                </div>
                            </div>
                            <p class="mb-1">${review.text || ''}</p>
                            <small class="text-muted">${new Date(review.created_at).toLocaleDateString()}</small>
                        </div>`;
                    });
                    html += '</div>';
                }
                break;

            case 'questions':
                // Для вопросов
                if (data.length === 0) {
                    html = '<p class="text-muted">Вопросов пока нет</p>';
                } else {
                    html = '<div class="questions-list">';
                    data.forEach(question => {
                        html += `
                        <div class="question-item border-bottom pb-3 mb-3">
                            <div class="d-flex align-items-center mb-2">
                                <strong class="me-2">${question.user_name}:</strong>
                                <span>${question.content}</span>
                            </div>
                            <small class="text-muted">${new Date(question.created_at).toLocaleDateString()}</small>

                            ${question.answers && question.answers.length > 0 ? `
                            <div class="answers mt-2 ms-4">
                                <strong>Ответы:</strong>
                                ${question.answers.map(answer => `
                                <div class="answer-item border-start border-3 ps-2 mt-2">
                                    <div class="d-flex align-items-center">
                                        <strong class="me-2">${answer.user_name}:</strong>
                                        <span>${answer.content}</span>
                                    </div>
                                    <small class="text-muted">${new Date(answer.created_at).toLocaleDateString()}</small>
                                </div>
                                `).join('')}
                            </div>
                            ` : ''}
                        </div>`;
                    });
                    html += '</div>';
                }
                break;

            case 'set':
                // Для товаров комплекта
                if (data.length === 0) {
                    html = '<p class="text-muted">Товары не найдены</p>';
                } else {
                    html = '<div class="row g-3">';
                    data.forEach(product => {
                        html += `
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="row g-0">
                                    <div class="col-4">
                                        ${product.image ? `<img src="${product.image}" class="img-fluid rounded-start h-100 object-fit-cover" alt="${product.title}">` :
                                        '<div class="bg-light d-flex align-items-center justify-content-center h-100"><i class="fas fa-image text-muted"></i></div>'}
                                    </div>
                                    <div class="col-8">
                                        <div class="card-body">
                                            <h6 class="card-title">${product.title}</h6>
                                            <p class="card-text text-primary fw-bold">${product.price} ₽</p>
                                            <small class="text-muted">${product.quantity > 0 ? 'В наличии' : 'Нет в наличии'}</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>`;
                    });
                    html += '</div>';
                }
                break;

            default:
                html = '<p class="text-muted">Данные не найдены</p>';
        }

        resultsContent.innerHTML = html;
    }

    // Функция закрытия результатов
    window.closeResults = function() {
        resultsContainer.style.display = 'none';
    };
});