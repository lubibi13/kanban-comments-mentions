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
    boards: List["Board"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.todo)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="tasks")

class Board(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="boards")
    columns: List["Column"] = Relationship(back_populates="board")

class Column(SQLModel, table=True):
    # explicit plural tablename: "column" is a reserved SQL keyword
    __tablename__ = "columns"
    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id")
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    board: Optional[Board] = Relationship(back_populates="columns")
    cards: List["Card"] = Relationship(back_populates="column")

class Card(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    column_id: int = Field(foreign_key="columns.id")
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    column: Optional[Column] = Relationship(back_populates="cards")

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

class BoardCreate(SQLModel):
    title: str

class BoardUpdate(SQLModel):
    title: Optional[str] = None

class BoardRead(SQLModel):
    id: int
    title: str
    created_at: datetime

class ColumnCreate(SQLModel):
    title: str

class ColumnUpdate(SQLModel):
    title: Optional[str] = None

class ColumnRead(SQLModel):
    id: int
    board_id: int
    title: str
    created_at: datetime

class CardCreate(SQLModel):
    title: str

class CardUpdate(SQLModel):
    title: Optional[str] = None
    column_id: Optional[int] = None

class CardRead(SQLModel):
    id: int
    column_id: int
    title: str
    created_at: datetime
