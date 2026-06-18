"""
Инкапсуляция: User скрывает внутреннее состояние за свойствами и методами.

Принципы ООП:
- Инкапсуляция: приватные поля _email, _role; доступ через @property
- Валидация данных при изменении состояния
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


@dataclass
class User:
    """Пользователь системы с инкапсулированным состоянием."""

    name: str
    _email: str = field(repr=False)
    _role: UserRole = field(default=UserRole.MEMBER, repr=False)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    _active: bool = field(default=True, repr=False)

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if "@" not in value:
            raise ValueError("Некорректный email")
        self._email = value

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def is_active(self) -> bool:
        return self._active

    def promote_to(self, new_role: UserRole) -> None:
        """Повышение роли — только admin может назначать admin."""
        if new_role == UserRole.ADMIN and self._role != UserRole.ADMIN:
            raise PermissionError("Только admin может назначать admin")
        self._role = new_role

    def deactivate(self) -> None:
        self._active = False

    def activate(self) -> None:
        self._active = True

    def can_manage_tasks(self) -> bool:
        return self._active and self._role in (UserRole.ADMIN, UserRole.MANAGER)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self._email,
            "role": self._role.value,
            "is_active": self._active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        user = cls(name=data["name"], _email=data["email"])
        user.id = data.get("id", user.id)
        user._role = UserRole(data.get("role", "member"))
        user._active = data.get("is_active", True)
        return user
