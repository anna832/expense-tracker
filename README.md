# Expense Tracker

[![CI](https://github.com/anna832/expense-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/anna832/expense-tracker/actions/workflows/ci.yml)

Проект для учёта расходов. 

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

## Стек технологий

| Слой | Технология |
|---|---|
| **Язык** | Python |
| **API** | FastAPI + SQLAlchemy + Pydantic |
| **Админка** | Django |
| **База данных** | PostgreSQL |
| **Аутентификация** | JWT (PyJWT) + bcrypt |
| **Тесты** | pytest + testcontainers + httpx |
| **Линтер / форматтер** | Ruff |
| **CI** | GitHub Actions |
| **Контейнеризация** | Docker + docker-compose |

---

## Архитектура

Django и FastAPI работают с одной базой, но у каждого своя роль:

- **Django** — админка, миграции и пользователи. Источник истины для схемы:
  все изменения таблиц идут только через Django-миграции.
- **FastAPI** — REST API: асинхронность, автодокументация, валидация Pydantic.
  Модели SQLAlchemy описывают те же таблицы и намеренно не создают их сами.

Цена решения — схема описана дважды и может разъехаться. Страховка: тесты
поднимают настоящий PostgreSQL через testcontainers и прогоняют по нему
Django-миграции, так что API тестируется на той же схеме, что и в продакшене.

---

## API Endpoints

| Метод | URL | Описание |
|---|---|---|
| POST | `/api/v1/auth/register/` | Регистрация |
| POST | `/api/v1/auth/login/` | Логин, возвращает JWT |
| GET | `/api/v1/auth/me/` | Текущий пользователь |
| GET | `/api/v1/categories/` | Список категорий |
| POST | `/api/v1/expenses/` | Создать расход |
| GET | `/api/v1/expenses/` | Список с пагинацией и фильтрами |
| GET | `/api/v1/expenses/{id}/` | Получить расход |
| PATCH | `/api/v1/expenses/{id}/` | Обновить расход |
| DELETE | `/api/v1/expenses/{id}/` | Удалить расход |
| GET | `/api/v1/reports/monthly/` | Сумма расходов за месяц |
| GET | `/api/v1/reports/by-categories/` | Разбивка по категориям |
| GET | `/health/` | Проверка работоспособности |

Все эндпоинты, кроме `/health/` и `/api/v1/auth/`, требуют JWT-токен.
Получить его — `POST /api/v1/auth/login/`, дальше передавать в заголовке:

    Authorization: Bearer <token>

В Swagger (`/docs`) для этого есть кнопка **Authorize** вверху страницы.