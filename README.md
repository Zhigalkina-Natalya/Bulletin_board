# Проект №6 Доска объявлений (Bulletin Board API)

---
## Описание проекта

REST API для доски объявлений с продвинутой системой пользователей,
прав доступа и асинхронной обработкой задач.

### Возможности

***Пользователи***

- Регистрация и JWT-аутентификация
- Профиль пользователя (редактирование только своего профиля)
- Роли:
   - **Администратор** — полный доступ
   - **Менеджер контента** — управление категориями
   - **Пользователь** — создание объявлений
   - **Анонимный пользователь** — только просмотр

***Объявления***

- CRUD операции
- Только автор может редактировать/удалять
- Загрузка изображений
- Превью изображений в админке
- Фильтрация:
   - по категории
   - по цене
- Поиск (title, description)
- Сортировка (price, created_at)
- Пагинация

***Категории***

- CRUD операции
- Управление доступом (только менеджер/админ)
- Inline объявления в админке

### Асинхронные задачи

- Celery + Redis
- Уведомление о создании объявления (фоновые задачи)

### Безопасность

- JWT авторизация
- CORS (настроен безопасно, без allow all)
- Разграничение прав доступа

---

## Технологии
- Python 3.13
- Django 6
- Django REST Framework
- PostgreSQL
- Docker & Docker Compose
- Redis
- Celery
- JWT (SimpleJWT)
- drf-spectacular (Swagger / OpenAPI)
- django-filter
- Pillow


---


---

## Установка, настройка, запуск (Docker)

1. Клонировать репозиторий

```
https://github.com/Zhigalkina-Natalya/Bulletin_board
```

2. Создать `.env` по образцу: `.env.sample`
Пример:
```
SECRET_KEY=your_secret_key
DEBUG=True

DB_NAME=bulletin_board
DB_USER=postgres
DB_PASSWORD=12345
DB_HOST=db
DB_PORT=5432

CELERY_BROKER_URL=redis://redis:6379/0

CORS_ALLOWED_ORIGINS=http://localhost:3000

```

3. Запуск проекта

```
docker compose up --build
```

**Будут запущены следующие контейнеры:**

- `web` - Django backend
- `db` PostgreSQL (db)
- `redis`- брокер
- `Celery` - воркер


**Приложение будет доступно по адресу:**

| Сервис      | URL                                     |
|-------------|-----------------------------------------|
| API         | http://localhost:8000/api/              |
| Swagger     | http://localhost:8000/api/docs/swagger/ |
| Redoc       | http://localhost:8000/api/docs/redoc/   |
| Admin       | http://localhost:8000/admin/            |



**Миграции применяются автоматически при запуске контейнера.**

**Важно! При изменении настроек БД необходимо запустить команды:**
```
docker-compose down -v
docker-compose up --build
```

4. Создать суперпользователя
```
docker-compose exec web python manage.py createadmin
```
---



## Авторизация

**Получение токена**
```
POST /api/token/
Body:
{
  "email": "admin@example.com",
  "password": "123456"
}
```

**Использование токена**

Authorization: Bearer <access_token>

**Обновление токена**

```
POST /api/token/refresh/
```

## Примеры API запросов

### Создать объявление:
```
POST /api/advertisements/ads/
Body:
{
  "title": "Продам квартиру",
  "description": "3-комнатная квартира",
  "price": 6000000,
  "category": 1
}
```

### Фильтрация

```
GET /api/advertisements/ads/?category=1&min_price=100000&max_price=700000
```

### Поиск

```
GET /api/advertisements/ads/?search=квартира
```

### Сортировка

```
GET /api/advertisements/ads/?ordering=price
```

---

## Тестирование

**Запуск тестов:**
```
poetry run python manage.py test
```

**Покрытие:**

```
coverage run manage.py test
coverage report
```

**Покрытие: > 80%**

---

## Структура проекта
bulletin_board/
├── advertisements/
├── users/
├── config/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env

---
---

##  Планы развития
- CI/CD (GitHub Actions)
- Email-уведомления
- Кэширование (Redis)
- Лайки/избранное
- WebSocket уведомления
- Frontend (React)
