"""FastAPI приложение — Task Manager с демонстрацией ООП."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

from models import EmailNotifier, PushNotifier, InAppNotifier
from services import NotificationService, TaskService

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Task Manager OOP Demo", version="1.0.0")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

notification_service = NotificationService([
    EmailNotifier(),
    PushNotifier(),
    InAppNotifier(),
])
task_service = TaskService(notification_service)


class CreateTaskRequest(BaseModel):
    title: str
    description: str = ""
    priority: str = "low"
    assignee_id: Optional[str] = None
    project_id: Optional[str] = None


class UpdateStatusRequest(BaseModel):
    status: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/tasks")
async def list_tasks(status: Optional[str] = None, priority: Optional[str] = None):
    from models import TaskStatus, TaskPriority
    s = TaskStatus(status) if status else None
    p = TaskPriority(priority) if priority else None
    return task_service.get_all_tasks(status=s, priority=p)


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(404, "Задача не найдена")
    return task


@app.post("/api/tasks")
async def create_task(body: CreateTaskRequest):
    return task_service.create_task(
        title=body.title,
        description=body.description,
        priority=body.priority,
        assignee_id=body.assignee_id,
        project_id=body.project_id,
    )


@app.patch("/api/tasks/{task_id}/status")
async def update_status(task_id: str, body: UpdateStatusRequest):
    try:
        return task_service.update_status(task_id, body.status)
    except KeyError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/api/users")
async def list_users():
    return task_service.get_users()


@app.get("/api/projects")
async def list_projects():
    return task_service.get_projects()


@app.get("/api/oop-demo")
async def oop_demo():
    """Демонстрация всех принципов ООП в JSON."""
    return task_service.get_oop_demo()


@app.get("/api/notifications/{email}")
async def get_notifications(email: str):
    return notification_service.get_in_app_notifications(email)
