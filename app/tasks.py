from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import Task, TaskCreate, TaskRead, TaskUpdate, User
from app.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskRead])
def list_tasks(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return session.exec(select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc())).all()

@router.post("/", response_model=TaskRead, status_code=201)
def create_task(payload: TaskCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    task = Task(**payload.model_dump(), user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return None
