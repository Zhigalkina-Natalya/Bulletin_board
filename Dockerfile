# Базовый образ
FROM python:3.13-slim
# отключаем создание .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# вывод логов без буфера
ENV PYTHONUNBUFFERED=1

# Рабочая директория
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y gcc libpq-dev libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY pyproject.toml poetry.lock* ./

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копируем проект
COPY . .

# Создаем пользователя для запуска приложения
RUN useradd -m appuser
RUN mkdir -p /app/media && chmod -R 777 /app/media
USER appuser

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
