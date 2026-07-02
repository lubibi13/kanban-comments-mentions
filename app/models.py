from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class TaskStatus(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.todo)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="tasks")

# API schemas (non-table)
class UserCreate(SQLModel):
    email: str
    password: str

class UserRead(SQLModel):
    id: int
    email: str
    created_at: datetime

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

class TaskRead(SQLModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime
