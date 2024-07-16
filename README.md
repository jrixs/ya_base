# Movie Library 

## Спринт 6: СЕРВИС AUTH

### Команда:
 - Юрий Сыновец
 - Андрей Николаев
 - Александра Волкова

### Схема:
![architecture](https://github.com/user-attachments/assets/a4204f4b-03eb-406d-8a02-8634f56744ff)

### Новые сервисы:
 - auth(fastapi)
 - auth_db(postgres)
 - auth_stotage(redis)

### Запуск тестов.
```bash
geral_async_API_sprint_1/tests/functional$ pytest
```

### Запуск тестов в контейнере.
```bash
geral_async_API_sprint_1/tests$ sudo docker compose up --abort-on-container-exit | grep tests
```

### Запуск всех сервисов.
```bash
geral_async_API_sprint_1$ sudo docker compose up -d --build
```
