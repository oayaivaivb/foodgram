# 🍲 Foodgram — продуктовый помощник

**Foodgram** — веб-приложение для публикации и поиска кулинарных рецептов.

Пользователи могут создавать собственные рецепты, добавлять рецепты в избранное, подписываться на авторов и формировать список покупок на основе выбранных блюд.

🌐 **Развёрнутый проект:** [foodgramm.sytes.net](https://foodgramm.sytes.net)

## ✨ Основные возможности

* 🍽️ Создание, редактирование и удаление рецептов
* 🏷️ Фильтрация рецептов по тегам
* ⭐ Добавление рецептов в избранное
* 👥 Подписка на авторов и просмотр ленты подписок
* 🛒 Формирование и скачивание списка покупок
* 🔗 Генерация коротких ссылок на рецепты
* 👤 Управление профилем и аватаром
* 🔐 Регистрация и аутентификация пользователей
* 📖 REST API для взаимодействия с приложением

## 🛠 Технологии

### Backend

* **Python**
* **Django 5.1.1**
* **Django REST Framework 3.15.2**
* **Djoser**
* **PostgreSQL 13**
* **Gunicorn**

### Frontend

* **React 18**
* **React Router**
* **Redux**

### Инфраструктура

* **Docker / Docker Compose**
* **Nginx**
* **GitHub Actions**
* **CI/CD**

## 🚀 Запуск проекта

### Локальная разработка

Клонирование репозитория:

```bash
git clone git@github.com:ваш_аккаунт/foodgram.git
cd foodgram
```

Создание виртуального окружения и установка зависимостей:

```bash
cd backend

python -m venv venv
source venv/bin/activate
# Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Создайте файл `.env` на основе `.env.example` и укажите необходимые параметры.

Примените миграции:

```bash
python manage.py migrate
```

Загрузите ингредиенты:

```bash
python manage.py import_ingredients
```

Запустите сервер:

```bash
python manage.py runserver
```

### Docker Compose

Сборка и запуск контейнеров:

```bash
cd infra
docker compose up -d
```

Применение миграций:

```bash
docker compose exec backend python manage.py migrate
```

Загрузка ингредиентов:

```bash
docker compose exec backend python manage.py import_ingredients
```

Сборка статики:

```bash
docker compose exec backend python manage.py collectstatic
```

Создание суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```

## 📚 API

Документация API:

https://foodgramm.sytes.net/api/docs/

Основные эндпоинты:

* `POST /api/users/` — регистрация пользователя
* `POST /api/auth/token/login/` — аутентификация
* `GET /api/recipes/` — получение списка рецептов
* `POST /api/recipes/` — создание рецепта
* `GET /api/tags/` — получение тегов
* `GET /api/ingredients/` — получение ингредиентов
* `PUT /api/users/me/avatar/` — управление аватаром
* `GET /api/users/subscriptions/` — подписки пользователя
* `POST /api/recipes/{id}/favorite/` — добавить рецепт в избранное
* `POST /api/recipes/{id}/shopping_cart/` — добавить рецепт в список покупок
* `GET /api/recipes/download_shopping_cart/` — скачать список покупок

## 🔐 Переменные окружения

Основные параметры конфигурации:

```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=your_password_here
DB_HOST=db
DB_PORT=5432

SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=localhost 127.0.0.1 foodgramm.sytes.net
```

## 📁 Структура проекта

```text
foodgram/
├── backend/              # Django backend и REST API
├── frontend/             # React-приложение
├── infra/                # Docker Compose и конфигурация Nginx
├── data/                 # Данные для первоначального наполнения
└── README.md
```
