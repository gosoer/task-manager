"""Модель проекта — группировка задач."""

from dataclasses import dataclass, field
from typing import List, Optional
import uuid


@dataclass
class Project:
    name: str
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    _task_ids: List[str] = field(default_factory=list, repr=False)

    def add_task(self, task_id: str) -> None:
        if task_id not in self._task_ids:
            self._task_ids.append(task_id)

    def remove_task(self, task_id: str) -> None:
        if task_id in self._task_ids:
            self._task_ids.remove(task_id)

    @property
    def task_count(self) -> int:
        return len(self._task_ids)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_count": self.task_count,
        }
