# Task Manager — демонстрация ООП на Python

Простой менеджер задач с веб-интерфейсом. В коде явно показаны все четыре принципа объектно-ориентированного программирования.

## Запуск

```bash
cd task_manager
pip install -r requirements.txt
uvicorn main:app --reload
```

Откройте http://127.0.0.1:8000

API-документация: http://127.0.0.1:8000/docs

## Принципы ООП в проекте

| Принцип | Где в коде | Что демонстрирует |
|---------|-----------|-------------------|
| **Инкапсуляция** | `models/user.py` | Приватные поля `_email`, `_role`; доступ через `@property`; валидация в setter |
| **Наследование** | `models/task.py` | `Task` → `LowPriorityTask`, `HighPriorityTask`, `CriticalTask` |
| **Полиморфизм** | `models/task.py`, `models/notifier.py` | Один метод — разное поведение: `deadline_days()`, `send()` |
| **Абстракция** | `models/task.py`, `models/notifier.py` | ABC-классы `Task` и `Notifier` с абстрактными методами |

## Структура

```
task_manager/
├── main.py                 # FastAPI, маршруты
├── models/
│   ├── task.py             # Иерархия задач (наследование, полиморфизм)
│   ├── user.py             # User с инкапсуляцией
│   ├── notifier.py         # ABC Notifier + реализации (абстракция, полиморфизм)
│   └── project.py
├── services/
│   ├── task_service.py     # Бизнес-логика
│   └── notification_service.py
├── templates/index.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## API

- `GET /api/tasks` — список задач (фильтры: `status`, `priority`)
- `POST /api/tasks` — создать задачу
- `PATCH /api/tasks/{id}/status` — сменить статус
- `GET /api/users` — пользователи
- `GET /api/oop-demo` — JSON с примерами всех принципов ООП

## Пример полиморфизма

```python
tasks: list[Task] = [
    LowPriorityTask(title="README"),
    HighPriorityTask(title="CI/CD"),
    CriticalTask(title="Bug fix"),
]

for task in tasks:
    print(task.deadline_days())  # 14, 7, 3 — один интерфейс, разное поведение
```
