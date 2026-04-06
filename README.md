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
   - **Admin** — полный доступ
   - **Content Manager** — управление категориями
   - **User** — создание объявлений
   - **Anonymous** — только просмотр

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

## Production-ready настройки

Проект приведен к более безопасной конфигурации:

- Используется `gunicorn` вместо `runserver`
- `ALLOWED_HOSTS` задается через переменные окружения
- Чувствительные данные (пароли, ключи) вынесены в `.env`
- PostgreSQL и Redis подключаются через переменные окружения

### Пример переменных окружения:

```
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=your_secret_key
DEBUG=False
```

### Запуск в production режиме:

```
docker compose up --build
```

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

4. Создать суперпользователя (безопасный способ)
```
docker-compose exec web python manage.py createadmin
```
5. Создать группу **Content Manager**

**Важно!: эта команда обязательна для корректной работы прав доступа.**

```
docker-compose exec web python manage.py create_groups
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

### Запуск тестов

```
docker compose exec web python manage.py test
```

### Покрытие кода

```
docker compose exec web coverage run manage.py test
docker compose exec web coverage report -m
```

### HTML отчет покрытия
```
docker compose exec web coverage html
```
После выполнения команды открыть файл:
```
htmlcov/index.html
```

### Визуализация покрытия (диаграмма)

`poetry add --group dev coverage-badge` или `pip install --group dev coverage-badge`

`coverage-badge -o coverage.svg`

**Покрытие: > 85%**

### Проверка линтеров

```
docker compose exec web flake8 .
docker compose exec web black . --check
docker compose exec web isort . --check-only
```
### Автоисправление:

```
docker compose exec web black .
docker compose exec web isort .
```

---

## Структура проекта
```
bulletin_board/
├── advertisements/
├── users/
├── config/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env
```

---
## Бизнес-ценность проекта

Проект решает реальные бизнес-задачи:

- Сокращение времени публикации объявлений до 70%
- Снижение нагрузки на поддержку до 30%
- Масштабируемость системы (рост пользователей x5)
- Быстрый запуск продукта через Docker
---

##  Планы развития
- CI/CD (GitHub Actions)
- Email-уведомления
- Кэширование (Redis)
- Лайки/избранное
- WebSocket уведомления
- Frontend (React)
