"""
Наследование и полиморфизм: иерархия задач с разным поведением.

Принципы ООП:
- Наследование: Task → LowPriorityTask, HighPriorityTask, CriticalTask
- Полиморфизм: каждый подкласс переопределяет deadline_days(), urgency_label()
- Абстракция: базовый Task задаёт общий контракт
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task(ABC):
    """Абстрактная базовая задача — общие поля и контракт для подклассов."""

    title: str
    description: str = ""
    assignee_id: Optional[str] = None
    project_id: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: TaskStatus = TaskStatus.TODO
    created_at: datetime = field(default_factory=datetime.now)

    @abstractmethod
    def priority(self) -> TaskPriority:
        pass

    @abstractmethod
    def deadline_days(self) -> int:
        """Сколько дней на выполнение — зависит от приоритета."""
        pass

    @abstractmethod
    def urgency_label(self) -> str:
        """Человекочитаемая метка срочности."""
        pass

    def deadline(self) -> datetime:
        return self.created_at + timedelta(days=self.deadline_days())

    def is_overdue(self) -> bool:
        if self.status == TaskStatus.DONE:
            return False
        return datetime.now() > self.deadline()

    def start(self) -> None:
        if self.status != TaskStatus.TODO:
            raise ValueError("Можно начать только задачу в статусе todo")
        self.status = TaskStatus.IN_PROGRESS

    def complete(self) -> None:
        if self.status == TaskStatus.CANCELLED:
            raise ValueError("Отменённую задачу нельзя завершить")
        self.status = TaskStatus.DONE

    def cancel(self) -> None:
        if self.status == TaskStatus.DONE:
            raise ValueError("Завершённую задачу нельзя отменить")
        self.status = TaskStatus.CANCELLED

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "assignee_id": self.assignee_id,
            "project_id": self.project_id,
            "status": self.status.value,
            "priority": self.priority().value,
            "deadline_days": self.deadline_days(),
            "urgency_label": self.urgency_label(),
            "deadline": self.deadline().isoformat(),
            "is_overdue": self.is_overdue(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class LowPriorityTask(Task):
    """Обычная задача — 14 дней на выполнение."""

    def priority(self) -> TaskPriority:
        return TaskPriority.LOW

    def deadline_days(self) -> int:
        return 14

    def urgency_label(self) -> str:
        return "Низкий приоритет"


@dataclass
class HighPriorityTask(Task):
    """Важная задача — 7 дней, требует внимания."""

    def priority(self) -> TaskPriority:
        return TaskPriority.HIGH

    def deadline_days(self) -> int:
        return 7

    def urgency_label(self) -> str:
        return "Высокий приоритет ⚡"


@dataclass
class CriticalTask(Task):
    """Критическая задача — 3 дня, блокирует релиз."""

    def priority(self) -> TaskPriority:
        return TaskPriority.CRITICAL

    def deadline_days(self) -> int:
        return 3

    def urgency_label(self) -> str:
        return "КРИТИЧНО 🔥"


def create_task(title: str, description: str, priority: TaskPriority, **kwargs) -> Task:
    """Фабрика задач — полиморфное создание нужного подкласса."""
    mapping = {
        TaskPriority.LOW: LowPriorityTask,
        TaskPriority.HIGH: HighPriorityTask,
        TaskPriority.CRITICAL: CriticalTask,
    }
    cls = mapping[priority]
    return cls(title=title, description=description, **kwargs)
