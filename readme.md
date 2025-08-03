# Django REST Framework: Учебный проект

Учебный проект в рамках практики по Django REST Framework.

## Описание

Это минимальный backend для онлайн-курсов на Django + DRF.

- Кастомный пользователь (email-авторизация, телефон, город, аватар)
- CRUD для курсов через ViewSet
- CRUD для уроков через generic views
- Хранение медиафайлов (картинки, аватары)
- Конфигурация через .env

## Быстрый старт

1. Клонируйте репозиторий и создайте виртуальное окружение:

    python -m venv .venv  
    source .venv/bin/activate  
    pip install -r requirements.txt

2. Скопируйте `.env_template` в `.env` и заполните переменные окружения.

3. Примените миграции:

    python manage.py migrate

4. Запустите сервер:

    python manage.py runserver

## Структура

- users/ — приложение пользователей
- study/ — курсы и уроки
- config/ — настройки Django
- .env_template — пример переменных окружения
