"""
Абстракция и полиморфизм: базовый класс Notifier и его реализации.

Принципы ООП:
- Абстракция: ABC Notifier задаёт контракт send()
- Полиморфизм: EmailNotifier, PushNotifier, InAppNotifier — разное поведение
  через один интерфейс
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class NotificationMessage:
    """Сообщение для отправки через любой канал."""

    recipient: str
    subject: str
    body: str
    created_at: datetime = field(default_factory=datetime.now)


class Notifier(ABC):
    """Абстрактный базовый класс — контракт для всех каналов уведомлений."""

    @abstractmethod
    def send(self, message: NotificationMessage) -> dict:
        """Отправить уведомление. Каждая реализация делает это по-своему."""
        pass

    @abstractmethod
    def channel_name(self) -> str:
        """Название канала для логирования и UI."""
        pass


class EmailNotifier(Notifier):
    """Отправка уведомлений по email."""

    def send(self, message: NotificationMessage) -> dict:
        return {
            "channel": self.channel_name(),
            "status": "sent",
            "detail": f"Email → {message.recipient}: {message.subject}",
        }

    def channel_name(self) -> str:
        return "email"


class PushNotifier(Notifier):
    """Push-уведомления на устройство."""

    def send(self, message: NotificationMessage) -> dict:
        return {
            "channel": self.channel_name(),
            "status": "sent",
            "detail": f"Push → {message.recipient}: {message.body[:50]}...",
        }

    def channel_name(self) -> str:
        return "push"


class InAppNotifier(Notifier):
    """Внутрисистемные уведомления (лента в приложении)."""

    def __init__(self) -> None:
        self._inbox: List[dict] = []

    def send(self, message: NotificationMessage) -> dict:
        entry = {
            "recipient": message.recipient,
            "subject": message.subject,
            "body": message.body,
            "read": False,
            "created_at": message.created_at.isoformat(),
        }
        self._inbox.append(entry)
        return {
            "channel": self.channel_name(),
            "status": "delivered",
            "detail": f"In-app → {message.recipient}: {message.subject}",
        }

    def channel_name(self) -> str:
        return "in_app"

    def get_inbox(self, recipient: str) -> List[dict]:
        return [n for n in self._inbox if n["recipient"] == recipient]
