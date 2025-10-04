// Конфигурация API
    const API_CONFIG = {
        baseUrl: '/garage',
        endpoints: {
            brands: '/api/brands/',
            models: '/api/models/',
            userCars: '/api/add-cars/',
            carDetail: '/api/detail-cars/'
        }
    };

    // Класс для работы с API
    class GarageAPI {
        static async getBrands() {
            try {
                const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.brands}`);
                if (!response.ok) throw new Error('Ошибка загрузки марок');
                return await response.json();
            } catch (error) {
                console.error('API Error:', error);
                throw error;
            }
        }

        static async getModels(brandId) {
            console.log(brandId);
            try {
                const response = await fetch(
                    `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.models}?brand_id=${brandId}`
                );
                console.log(response);
                if (!response.ok) throw new Error('Ошибка загрузки моделей');
                return await response.json();
            } catch (error) {
                console.error('API Error:', error);
                throw error;
            }
        }

        static async addCar(carData) {
            try {
                const csrfToken = this.getCSRFToken();
                const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.userCars}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify(carData)
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || data.error || 'Ошибка сервера');
                }

                return { success: true, data };
            } catch (error) {
                console.error('API Error:', error);
                return { success: false, error: error.message };
            }
        }

        static async updateCar(carId, carData) {
            try {
                const csrfToken = this.getCSRFToken();
                const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.carDetail}${carId}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify(carData)
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || data.error || 'Ошибка обновления');
                }

                return { success: true, data };
            } catch (error) {
                console.error('API Error:', error);
                return { success: false, error: error.message };
            }
        }

        static async deleteCar(carId) {
            try {
                const csrfToken = this.getCSRFToken();
                const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.carDetail}${carId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': csrfToken,
                    }
                });

                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.detail || data.error || 'Ошибка удаления');
                }

                return { success: true };
            } catch (error) {
                console.error('API Error:', error);
                return { success: false, error: error.message };
            }
        }

        static async setPrimaryCar(carId) {
            return await this.updateCar(carId, { is_main: true });
        }

        static getCSRFToken() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]');
            return token ? token.value : '';
        }
    }

    // Управление формой быстрого добавления
    class QuickAddCarForm {
        constructor(formId) {
            this.form = document.getElementById(formId);
            if (!this.form) return;

            this.brandSelect = this.form.querySelector('#brand-select');
            this.modelSelect = this.form.querySelector('#model-select');
            this.isMainCheckbox = this.form.querySelector('#is_main');
            this.submitBtn = this.form.querySelector('#submit-btn');
            this.loadingDiv = this.form.querySelector('#loading-models');
            this.errorsDiv = this.form.querySelector('#form-errors');
            this.successDiv = this.form.querySelector('#form-success');

            this.init();
        }

        async init() {
            await this.loadBrands();
            this.setupEventListeners();
        }

        async loadBrands() {
            try {
                const brands = await GarageAPI.getBrands();
                this.populateBrands(brands);
            } catch (error) {
                this.showError('Ошибка загрузки марок автомобилей');
            }
        }

        populateBrands(brands) {
            this.brandSelect.innerHTML = '<option value="">Выберите марку</option>';
            brands.forEach(brand => {
                const option = document.createElement('option');
                option.value = brand.id;
                option.textContent = brand.name;
                this.brandSelect.appendChild(option);
            });
        }

        async loadModels(brandId) {
            this.showLoading();
            this.modelSelect.disabled = true;
            this.submitBtn.disabled = true;

            try {
                const models = await GarageAPI.getModels(brandId);
                this.populateModels(models);
                this.hideLoading();
            } catch (error) {
                this.showError('Ошибка загрузки моделей');
                this.hideLoading();
            }
        }

        populateModels(responseData) {
            const models = responseData.models;


            this.modelSelect.innerHTML = '<option value="">Выберите модель</option>';

            if (models) {
                models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    this.modelSelect.appendChild(option);
                });
                this.modelSelect.disabled = false;

            } else {
                this.modelSelect.innerHTML = '<option value="">Модели не найдены</option>';
                this.modelSelect.disabled = true;
            }
        }

        setupEventListeners() {
            this.brandSelect.addEventListener('change', (e) => {
                console.log(e.target);
                const brandId = e.target.value;
                if (brandId) {
                    this.loadModels(brandId);
                } else {
                    this.modelSelect.innerHTML = '<option value="">Сначала выберите марку</option>';
                    this.modelSelect.disabled = true;
                    this.submitBtn.disabled = true;
                }
            });

            this.modelSelect.addEventListener('change', (e) => {
                this.submitBtn.disabled = !e.target.value;
            });

            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        async handleSubmit(e) {
            e.preventDefault();

            const formData = {
                car_model: parseInt(this.modelSelect.value),
                is_main: this.isMainCheckbox.checked
            };

            if (!formData.car_model) {
                this.showError('Пожалуйста, выберите модель автомобиля');
                return;
            }

            this.setLoadingState(true);

            const result = await GarageAPI.addCar(formData);

            if (result.success) {
                this.showSuccess('Автомобиль успешно добавлен в гараж!');
                this.resetForm();
                setTimeout(() => window.location.reload(), 1500);
            } else {
                this.showError(result.error || 'Ошибка при добавлении автомобиля');
            }

            this.setLoadingState(false);
        }

        resetForm() {
            this.brandSelect.value = '';
            this.modelSelect.innerHTML = '<option value="">Сначала выберите марку</option>';
            this.modelSelect.disabled = true;
            this.isMainCheckbox.checked = false;
            this.submitBtn.disabled = true;
        }

        setLoadingState(isLoading) {
            this.submitBtn.disabled = isLoading;
            this.submitBtn.innerHTML = isLoading
                ? '<i class="fas fa-spinner fa-spin"></i> Добавление...'
                : '<i class="fas fa-plus"></i> Добавить в гараж';
        }

        showLoading() {
            if (this.loadingDiv) this.loadingDiv.classList.remove('d-none');
        }

        hideLoading() {
            if (this.loadingDiv) this.loadingDiv.classList.add('d-none');
        }

        showError(message) {
            if (this.errorsDiv) {
                this.errorsDiv.textContent = message;
                this.errorsDiv.classList.remove('d-none');
                if (this.successDiv) this.successDiv.classList.add('d-none');
            }
        }

        showSuccess(message) {
            if (this.successDiv) {
                this.successDiv.textContent = message;
                this.successDiv.classList.remove('d-none');
                if (this.errorsDiv) this.errorsDiv.classList.add('d-none');
            }
        }
    }

    // Управление автомобилями в гараже
    class CarManager {
        constructor() {
            this.setupEventListeners();
        }

        setupEventListeners() {
            document.addEventListener('click', (e) => {
                if (e.target.closest('.set-primary-btn')) {
                    const button = e.target.closest('.set-primary-btn');
                    const carId = button.dataset.carId;
                    this.setAsPrimary(carId, button);
                }

                if (e.target.closest('.delete-car-btn')) {
                    const button = e.target.closest('.delete-car-btn');
                    const carId = button.dataset.carId;
                    const carName = button.dataset.carName;
                    this.deleteCar(carId, carName, button);
                }
            });
        }

        async setAsPrimary(carId, button) {
            const originalText = button.innerHTML;

            try {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

                const result = await GarageAPI.setPrimaryCar(carId);

                if (result.success) {
                    this.showNotification('Автомобиль установлен как основной!', 'success');
                    this.updateUIAfterPrimarySet(carId);
                } else {
                    this.showNotification(result.error, 'error');
                }
            } catch (error) {
                this.showNotification('Ошибка при обновлении', 'error');
            } finally {
                button.disabled = false;
                button.innerHTML = originalText;
            }
        }

        async deleteCar(carId, carName, button) {
            if (!confirm(`Вы уверены, что хотите удалить "${carName}" из гаража?`)) {
                return;
            }

            const originalText = button.innerHTML;

            try {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

                const result = await GarageAPI.deleteCar(carId);

                if (result.success) {
                    this.showNotification('Автомобиль удален из гаража', 'success');
                    button.closest('.car-card').remove();

                    // Если удалили все автомобили, показываем сообщение
                    if (!document.querySelector('.car-card')) {
                        this.showEmptyGarageMessage();
                    }
                } else {
                    this.showNotification(result.error, 'error');
                }
            } catch (error) {
                this.showNotification('Ошибка при удалении', 'error');
            } finally {
                button.disabled = false;
                button.innerHTML = originalText;
            }
        }

    updateUIAfterPrimarySet(primaryCarId) {

    // 1. Находим все элементы
    const allButtons = document.querySelectorAll('.car-action');
    console.log(allButtons);
    const allCards = document.querySelectorAll('.car-card');

    // 2. Сбрасываем все к исходному состоянию
    allButtons.forEach(btn => {
        btn.disabled = false;
        btn.innerHTML = '<i class="far fa-star me-1"></i>Сделать основным';
        console.log(btn);
    });

    allCards.forEach(card => {
        card.classList.remove('primary-car', 'border-warning');

        // Находим ВСЕ бейджи с классом bg-warning
        const statusBadges = card.querySelectorAll('.badge.bg-warning');
        console.log('Found badges:', statusBadges.length);

        statusBadges.forEach(badge => {
            // Проверяем что это бейдж статуса (содержит "Основной" или "Дополнительный")
            if (badge.textContent.includes('Основной') || badge.textContent.includes('Дополнительный')) {
                // Меняем на "Дополнительный"
                badge.innerHTML = '<i class="fas fa-car me-1"></i>Дополнительный';
                badge.className = 'badge bg-secondary';
            }
        });
    });

    // 3. Находим и обновляем основной автомобиль
    const primaryButton = document.querySelector(`[data-car-id="${primaryCarId}"]`);
    if (primaryButton) {
        const primaryCard = primaryButton.closest('.car-card');

        if (primaryCard) {
            // Выделяем карточку
            primaryCard.classList.add('primary-car', 'border-warning');

            // Добавляем бейдж
            const title = primaryCard.querySelector('.car-status');
            const badge = title.querySelector('.badge.bg-secondary');
            badge.remove();
            if (title) {
                const badge = document.createElement('span');
                badge.className = 'badge bg-warning ms-2';
                badge.innerHTML = '<i class="fas fa-star me-1"></i>Основной';
                title.appendChild(badge);
            }

            const basicBtn = primaryCard.querySelector('.car-action');
            console.log(basicBtn);
            // Обновляем кнопку
            primaryButton.disabled = true;
            primaryButton.innerHTML = '<i class="fas fa-star text-warning me-1"></i>Основной';
        }
    }
}

        showEmptyGarageMessage() {
            const garageContainer = document.querySelector('.garage-container');
            if (garageContainer) {
                garageContainer.innerHTML = `
                    <div class="text-center py-5">
                        <i class="fas fa-garage-car fa-3x text-muted mb-3"></i>
                        <h4>Гараж пуст</h4>
                        <p class="text-muted">Добавьте свой первый автомобиль</p>
                    </div>
                `;
            }
        }

        showNotification(message, type = 'info') {
            // Используем Bootstrap alerts если есть
            const alertClass = type === 'error' ? 'danger' : type;
            const notification = document.createElement('div');
            notification.className = `alert alert-${alertClass} alert-dismissible fade show mt-3`;
            notification.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            const container = document.getElementById('notifications') || document.querySelector('.container');
            container.prepend(notification);

            setTimeout(() => notification.remove(), 5000);
        }
    }

    // Инициализация при загрузке страницы
    document.addEventListener('DOMContentLoaded', () => {
        // Инициализация формы добавления
        new QuickAddCarForm('quick-add-car-form');

        // Инициализация менеджера автомобилей
        new CarManager();
    });