"""
Сервис задач — бизнес-логика поверх ООП-моделей.

Демонстрирует: работу с полиморфными Task-подклассами через единый интерфейс.
"""

from typing import Dict, List, Optional

from models.task import Task, TaskStatus, TaskPriority, create_task
from models.user import User, UserRole
from models.project import Project
from services.notification_service import NotificationService


class TaskService:
    def __init__(self, notification_service: NotificationService) -> None:
        self._tasks: Dict[str, Task] = {}
        self._users: Dict[str, User] = {}
        self._projects: Dict[str, Project] = {}
        self._notifications = notification_service
        self._seed_data()

    def _seed_data(self) -> None:
        admin = User(name="Алексей", _email="alex@example.com", _role=UserRole.ADMIN)
        member = User(name="Мария", _email="maria@example.com")
        self._users[admin.id] = admin
        self._users[member.id] = member

        project = Project(name="Веб-приложение", description="Разработка MVP")
        self._projects[project.id] = project

        tasks = [
            create_task("Настроить CI/CD", "GitHub Actions pipeline", TaskPriority.HIGH, assignee_id=member.id, project_id=project.id),
            create_task("Написать README", "Документация проекта", TaskPriority.LOW, assignee_id=member.id, project_id=project.id),
            create_task("Исправить баг авторизации", "401 при refresh token", TaskPriority.CRITICAL, assignee_id=member.id, project_id=project.id),
        ]
        for t in tasks:
            self._tasks[t.id] = t
            project.add_task(t.id)

    def get_all_tasks(self, status: Optional[TaskStatus] = None, priority: Optional[TaskPriority] = None) -> List[dict]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority() == priority]
        return [t.to_dict() for t in tasks]

    def get_task(self, task_id: str) -> Optional[dict]:
        task = self._tasks.get(task_id)
        return task.to_dict() if task else None

    def create_task(self, title: str, description: str, priority: str, assignee_id: Optional[str] = None, project_id: Optional[str] = None) -> dict:
        task = create_task(
            title=title,
            description=description,
            priority=TaskPriority(priority),
            assignee_id=assignee_id,
            project_id=project_id,
        )
        self._tasks[task.id] = task
        if project_id and project_id in self._projects:
            self._projects[project_id].add_task(task.id)
        if assignee_id and assignee_id in self._users:
            user = self._users[assignee_id]
            self._notifications.notify_task_assigned(task, user)
        return task.to_dict()

    def update_status(self, task_id: str, new_status: str) -> dict:
        task = self._tasks.get(task_id)
        if not task:
            raise KeyError(f"Задача {task_id} не найдена")
        status = TaskStatus(new_status)
        if status == TaskStatus.IN_PROGRESS:
            task.start()
        elif status == TaskStatus.DONE:
            task.complete()
            if task.assignee_id:
                assignee = self._users.get(task.assignee_id)
                if assignee:
                    admin = next((u for u in self._users.values() if u.can_manage_tasks()), None)
                    if admin:
                        self._notifications.notify_task_completed(task, admin.email)
        elif status == TaskStatus.CANCELLED:
            task.cancel()
        return task.to_dict()

    def get_users(self) -> List[dict]:
        return [u.to_dict() for u in self._users.values()]

    def get_projects(self) -> List[dict]:
        return [p.to_dict() for p in self._projects.values()]

    def get_oop_demo(self) -> dict:
        """Эндпоинт для демонстрации принципов ООП в runtime."""
        sample_tasks = list(self._tasks.values())
        polymorphism_demo = [
            {
                "class": type(t).__name__,
                "title": t.title,
                "priority": t.priority().value,
                "deadline_days": t.deadline_days(),
                "urgency_label": t.urgency_label(),
            }
            for t in sample_tasks
        ]
        return {
            "encapsulation": {
                "description": "User скрывает _email, _role; доступ через @property",
                "example": self._users[list(self._users.keys())[0]].to_dict(),
            },
            "inheritance": {
                "description": "Task → LowPriorityTask, HighPriorityTask, CriticalTask",
                "hierarchy": ["Task (ABC)", "├── LowPriorityTask", "├── HighPriorityTask", "└── CriticalTask"],
            },
            "polymorphism": {
                "description": "Один метод deadline_days() — разный результат у подклассов",
                "examples": polymorphism_demo,
            },
            "abstraction": {
                "description": "Notifier (ABC) — контракт send(); реализации: Email, Push, InApp",
                "channels": self._notifications.available_channels(),
            },
        }
