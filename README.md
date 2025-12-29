TODO API + WebSocket + Фоновая задача

## Цель работы

Разработать полноценный серверный backend на FastAPI, реализующий:

### Функциональность

- **REST API** для управления списком задач (TODO-list)

  - `GET /tasks` — список всех задач
  - `GET /tasks/{id}` — получить одну задачу
  - `POST /tasks` — создать новую задачу
  - `PATCH /tasks/{id}` — частичное обновление задачи
  - `DELETE /tasks/{id}` — удалить задачу
  - `POST /task-generator/run` — принудительно вызвать фоновую задачу

- **WebSocket-канал** для уведомлений клиентов в реальном времени

  - `GET /ws/tasks` — подключение к потоку событий задач
  - События: `task_created`, `task_updated`, `task_deleted`

- **Фоновую задачу**, которая периодически наполняет базу данных

  - Загрузка данных со сторонних источников через `httpx`
  - Асинхронное добавление задач в БД

- **Асинхронная работа с базой данных** — SQLAlchemy + asyncpg

### Стек технологий

- **Backend**: FastAPI 0.123+, Uvicorn
- **Database**: PostgreSQL 16, SQLAlchemy 2.0+ (async)
- **ORM Migrations**: Alembic
- **WebSocket**: Starlette WebSocket
- **HTTP Client**: httpx
- **Config**: Pydantic Settings
- **Containerization**: Docker, Docker Compose

---

## Быстрый старт (Docker Compose)

### Требования

- Docker и Docker Compose

### Установка и запуск

1. **Склонировать репозиторий:**

   ```bash
   git clone https://github.com/c0ldhand/Parser.git
   ```

2. **Запустить приложение с помощью Docker Compose:**
   ```bash
   docker-compose up -d
   ```

## Структура проекта

```
Parser/
├── app/
│   ├── api/
│   │   ├── background_task_endpoints.py
│   │   │   └── HTTP-эндпоинт для ручного запуска фоновой задачи
│   │   │       обновления курсов валют (POST /tasks/run).
│   │   │
│   │   ├── currency_endpoints.py
│   │   │   └── REST API для работы с курсами валют:
│   │   │       получение списка, создание, обновление и удаление.
│   │   │
│   │   ├── websocket_endpoints.py
│   │   │   └── WebSocket эндпоинт (/ws/currencies)
│   │   │       для уведомлений клиентов в реальном времени.
│   │   │
│   │   └── nats_test.py
│   │       └── Тестовый эндпоинт для отправки сообщений
│   │           в NATS (эмуляция внешнего сервиса).
│   │
│   ├── database/
│   │   ├── models/
│   │   │   └── currency.py
│   │   │       └── ORM-модель CurrencyRate
│   │   │           (id, currency, rate, timestamp).
│   │   │
│   │   ├── init_db.py
│   │   │   └── Инициализация базы данных при старте приложения
│   │   │       (создание таблиц).
│   │   │
│   │   └── session.py
│   │       └── Асинхронный engine и sessionmaker SQLAlchemy.
│   │
│   ├── nats/
│   │   ├── client.py
│   │   │   └── Клиент NATS:
│   │   │       подключение, подписка, публикация сообщений
│   │   │       и обработка входящих событий.
│   │   │
│   │   └── nats_events.py
│   │       └── Вспомогательные функции для публикации
│   │           событий изменения курсов валют в NATS.
│   │
│   ├── schemas/
│   │   ├── currency.py
│   │   │   └── Pydantic-схемы:
│   │   │       CurrencyRateCreate,
│   │   │       CurrencyRateUpdate,
│   │   │       CurrencyRateOut.
│   │   │
│   │   └── ws_events.py
│   │       └── WebSocket-события:
│   │           CurrencyEventType (enum),
│   │           CurrencyEvent.
│   │
│   ├── tasks/
│   │   └── cbr_rates.py
│   │       └── Фоновая задача:
│   │           - HTTP-запрос к API ЦБ РФ
│   │           - парсинг XML
│   │           - обновление базы данных
│   │           - публикация событий в NATS
│   │           - периодический запуск через asyncio.
│   │
│   ├── ws/
│   │   └── connection_manager.py
│   │       └── Менеджер WebSocket-соединений
│   │           (подключение, отключение, broadcast сообщений).
│   │
│   ├── config.py
│   │   └── Конфигурация приложения
│   │       (Pydantic Settings, переменные окружения).
│   │
│   └── main.py
│       └── Точка входа FastAPI-приложения:
│           - lifespan
│           - запуск фоновой задачи
│           - подключение NATS
│           - регистрация роутеров.
│
├── data/
│   └── currencies.db
│       └── Файл базы данных SQLite
│           (создаётся автоматически).
│
├── venv/
│   └── Виртуальное окружение Python (не используется в Docker).
│
│
├── .env.example
│   └── Пример файла переменных окружения.
│
├── .dockerignore
│   └── Исключения для Docker.
│
├── .gitignore
│   └── Исключения для Git
│       (venv, .env, база данных и т.д.).
│
├── docker-compose.yml
│   └── Docker Compose конфигурация
│       (FastAPI-приложение + NATS).
│
├── Dockerfile
│   └── Docker-образ FastAPI-приложения.
│
├── requirements.txt
│   └── Python-зависимости проекта.
│
└── README.md
│   └── Описание проекта, инструкция по запуску,
│       документация API и примеры работы WebSocket и NATS.
                     # Этот файл
```

Swagger
<img width="1919" height="668" alt="image" src="https://github.com/user-attachments/assets/cc95ec7a-5bb5-4a48-861b-e6d3419089d8" />

Websocket
<img width="1118" height="208" alt="image" src="https://github.com/user-attachments/assets/874477ad-c863-4336-831c-b4190f1bfaad" />
