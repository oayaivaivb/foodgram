
# Foodgram - продуктовый помощник
[![Django](https://img.shields.io/badge/Django-5.1.1-092E20?logo=django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.15.2-a30000?logo=django)](https://www.django-rest-framework.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-336791?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10-2496ED?logo=docker)](https://www.docker.com/)
[![Nginx](https://img.shields.io/badge/Nginx-1.22.1-009639?logo=nginx)](https://nginx.org/)

## 🌐 Ссылка на развернутый проект

[https://foodgramm.sytes.net](https://foodgramm.sytes.net)

## 📝 Описание проекта

Foodgram — это веб-приложение, позволяющее пользователям публиковать свои кулинарные рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и формировать список покупок на основе выбранных рецептов.

### Основные функции:

- 🍽️ **Рецепты**: Создание, редактирование, просмотр и удаление рецептов
- 🏷️ **Теги**: Фильтрация рецептов по тегам (завтрак, обед, ужин и др.)
- ⭐ **Избранное**: Добавление понравившихся рецептов в список избранного
- 👥 **Подписки**: Возможность подписываться на других авторов
- 🛒 **Список покупок**: Добавление рецептов в список покупок с возможностью скачать список ингредиентов в формате TXT
- 🔗 **Короткие ссылки**: Получение короткой ссылки на любой рецепт
- 👤 **Профиль пользователя**: Возможность установки аватара, смена пароля

### Страницы проекта:

- Главная страница (список рецептов с пагинацией)
- Страница рецепта
- Страница пользователя
- Страница подписок
- Избранное
- Список покупок
- Создание/редактирование рецепта
- Смена пароля
- Статические страницы (О проекте, Технологии)

## 🛠️ Стек технологий

### Бэкенд
- **Django 5.1.1** — основной фреймворк
- **Django REST Framework 3.15.2** — создание REST API
- **Djoser** — аутентификация и управление пользователями
- **PostgreSQL 13** — база данных
- **Gunicorn** — WSGI-сервер

### Фронтенд
- **React 18** — одностраничное приложение (SPA)
- **React Router** — маршрутизация
- **Redux** — управление состоянием

### Инфраструктура
- **Docker** — контейнеризация
- **Docker Compose** — оркестрация контейнеров
- **Nginx** — веб-сервер и проксирование
- **GitHub Actions** — CI/CD (автоматическое тестирование и деплой)

## 🚀 Как развернуть проект

### Локальная разработка

1. **Клонирование репозитория**
   ```bash
   git clone git@github.com:ваш_аккаунт/foodgram.git
   cd foodgram
   ```

2. **Настройка виртуального окружения**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # для Linux/MacOS
   # venv\Scripts\activate   # для Windows
   pip install -r requirements.txt
   ```

3. **Создание файла `.env`**
   ```bash
   cp .env.example .env
   ```
   Заполните файл необходимыми переменными (см. раздел "Переменные окружения").

4. **Выполнение миграций**
   ```bash
   python manage.py migrate
   ```

5. **Загрузка тестовых данных**
   ```bash
   python manage.py import_ingredients
   ```

6. **Запуск локального сервера**
   ```bash
   python manage.py runserver
   ```

### Запуск через Docker Compose

1. **Сборка и запуск контейнеров**
   ```bash
   cd infra
   docker compose up -d
   ```

2. **Применение миграций**
   ```bash
   docker compose exec backend python manage.py migrate
   ```

3. **Загрузка ингредиентов**
   ```bash
   docker compose exec backend python manage.py import_ingredients
   ```

4. **Сборка статики**
   ```bash
   docker compose exec backend python manage.py collectstatic
   ```

5. **Создание суперпользователя**
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

## 📦 Загрузка тестовых данных

Для предзагрузки ингредиентов используйте команду:

```bash
python manage.py import_ingredients
```

Файл с ингредиентами должен находиться по пути `backend/data/ingredients.json` или `backend/data/ingredients.csv`.

## 🔐 Переменные окружения (.env)

Создайте файл `.env` в корне проекта со следующими переменными:

```env
# PostgreSQL
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=your_password_here
DB_HOST=db
DB_PORT=5432

# Django
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=localhost 127.0.0.1 foodgramm.sytes.net
```

## 📚 Документация API

Полная спецификация API доступна по адресу:
[https://foodgramm.sytes.net/api/docs/](https://foodgramm.sytes.net/api/docs/)

### Основные эндпоинты:

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/api/users/` | POST | Регистрация пользователя |
| `/api/auth/token/login/` | POST | Получение токена |
| `/api/recipes/` | GET | Список рецептов |
| `/api/recipes/` | POST | Создание рецепта |
| `/api/tags/` | GET | Список тегов |
| `/api/ingredients/` | GET | Список ингредиентов |
| `/api/users/me/avatar/` | PUT | Добавление аватара |
| `/api/users/subscriptions/` | GET | Мои подписки |
| `/api/recipes/{id}/favorite/` | POST/DELETE | Избранное |
| `/api/recipes/{id}/shopping_cart/` | POST/DELETE | Список покупок |
| `/api/recipes/download_shopping_cart/` | GET | Скачать список покупок |

## 👨‍💻 Автор

**Михайлов Александр**
- GitHub: [oayaivaivb](https://github.com/oayaivaivb)
- tg: [vlhkm](https://t.me/vlhkm)


