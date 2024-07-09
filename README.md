# Movie Library

### 

## Описание

Проектное задание пятого спринта. Командная работа.

Команда:
 - Юрий Сыновец
 - Андрей Николаев

## Новые сервисы
 - tests


## Разработка тестов
- для разработки запустите контейнеры, предворительно прокинув порты в файле docker-compose.yml сервисов на ружу.
```bash
geral_async_API_sprint_1/tests$ sudo docker compose up -d --build
```
- запуск тестов
```bash
geral_async_API_sprint_1/tests/functional$ pytest
```

## Запуск тестов в контейнере.
```bash
geral_async_API_sprint_1/tests$ sudo docker compose up --abort-on-container-exit | grep tests
```
