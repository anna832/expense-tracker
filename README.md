# Expense Tracker

Пет-проект для учёта расходов. 

---

## Технологии

| Технология | Назначение |
|---|---|
| Django | Админка, миграции |
| FastAPI | REST API |
| SQLAlchemy | ORM для FastAPI |
| Pydantic | Валидация данных API |
| PostgreSQL | База данных |
| Docker, Docker Compose | Запуск всех сервисов |
| pytest | Тесты |

---

## Как запустить

1. Клонируйте репозиторий

2. Создайте файл `.env` скопировав шаблон `.env.example` и подставив свои значения

3. Запустите через Docker

```bash
docker compose up --build -d
```

4. Создайте суперпользователя для Django Admin

```bash
docker compose exec django python manage.py createsuperuser
```

---

## Доступ

| Сервис | URL |
|---|---|
| Django Admin | http://127.0.0.1:8000/admin/ |
| FastAPI Swagger | http://127.0.0.1:8001/docs |
| PostgreSQL | localhost:5432 |

---

## API Endpoints

| Метод | URL | Описание |
|---|---|---|
| GET | `/api/v1/health/` | Проверка работоспособности |
| GET | `/api/v1/categories/` | Список категорий |
| POST | `/api/v1/expenses/` | Создать расход |
| GET | `/api/v1/expenses/` | Список расходов |
| GET | `/api/v1/expenses/{id}/` | Получить расход |
| PATCH | `/api/v1/expenses/{id}/` | Обновить расход |
| DELETE | `/api/v1/expenses/{id}/` | Удалить расход |
| GET | `/api/v1/reports/monthly/` | Общая сумма за месяц |
| GET | `/api/v1/reports/by-categories/` | Суммы по категориям |
