# Movie Library

### Асинхронный API для кинотеатра. Этот сервис будет точкой входа для всех клиентов.

## Описание

Проектное задание четвёртого спринта. Командная работа.

Команда:
 - Юрий Сыновец
 - Андрей Николаев

## Новые сервисы
 - redis
 - FastAPI

## Запуск прилодения

1. Добавление секретов.

    Секреты для подключения к БД:
    ```bash
    cat app/.env
    DEBUG=False
    DB_NAME=movies_database
    DB_USER=app
    DB_PASSWORD=password
    DB_HOST=db
    SECRET_KEY=******
    ```
    Пароль для сборки контейнера БД:
    ```bash
    echo "password" > app/db_pass
    ```

2. Сборка образа.
    ```bash
    sudo docker-compose up -d --build
    ```
