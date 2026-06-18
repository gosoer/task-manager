"""
Сервис уведомлений — полиморфная отправка через любой Notifier.

Демонстрирует: полиморфизм (один метод notify_all для разных каналов),
             инкапсуляцию (список notifiers скрыт внутри сервиса).
"""

from typing import List, Optional

from models.notifier import Notifier, NotificationMessage, InAppNotifier
from models.task import Task
from models.user import User


class NotificationService:
    def __init__(self, notifiers: Optional[List[Notifier]] = None) -> None:
        self._notifiers: List[Notifier] = notifiers or []
        self._in_app: Optional[InAppNotifier] = None
        for n in self._notifiers:
            if isinstance(n, InAppNotifier):
                self._in_app = n

    def add_notifier(self, notifier: Notifier) -> None:
        self._notifiers.append(notifier)
        if isinstance(notifier, InAppNotifier):
            self._in_app = notifier

    def notify_task_assigned(self, task: Task, user: User) -> List[dict]:
        """Полиморфизм: один вызов — все каналы обрабатывают по-своему."""
        message = NotificationMessage(
            recipient=user.email,
            subject=f"Новая задача: {task.title}",
            body=(
                f"Вам назначена задача «{task.title}».\n"
                f"Приоритет: {task.urgency_label()}\n"
                f"Дедлайн: {task.deadline().strftime('%d.%m.%Y')}"
            ),
        )
        return self._broadcast(message)

    def notify_task_completed(self, task: Task, manager_email: str) -> List[dict]:
        message = NotificationMessage(
            recipient=manager_email,
            subject=f"Задача выполнена: {task.title}",
            body=f"Задача «{task.title}» переведена в статус done.",
        )
        return self._broadcast(message)

    def _broadcast(self, message: NotificationMessage) -> List[dict]:
        results = []
        for notifier in self._notifiers:
            results.append(notifier.send(message))
        return results

    def get_in_app_notifications(self, email: str) -> List[dict]:
        if self._in_app:
            return self._in_app.get_inbox(email)
        return []

    def available_channels(self) -> List[str]:
        return [n.channel_name() for n in self._notifiers]
