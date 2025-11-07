# HMparts

Automotive parts website

# Создание виртуального окружения

python -m venv .venv

# Активация (Linux/Mac)

source venv/bin/activate

# Активация (Windows)

venv\Scripts\activate

# Установка зависимостей в виртуальном окружении

pip install -r requirements.txt

# Инициализация БД

1. Необходимо изменить данные в DATABASE app/settings.py на свои
2. Необходимо изменить данные super_db_config scripts/settings.py на свои от пользователя postgres
3. Запустит скрипт из файла run_db.py

# Запуск отладочного сервера

python manage.py runserver