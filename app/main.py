from fastapi import FastAPI
from app.db import init_db
from app.auth import router as auth_router
from app.tasks import router as tasks_router
from app.boards import router as boards_router
from app.columns import router as columns_router
from app.cards import router as cards_router
from app.comments import router as comments_router
from app.notifications import router as notifications_router

app = FastAPI(title="Task Starter API", version="0.1.0")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Task Starter API", "docs": "/docs"}

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(boards_router)
app.include_router(columns_router)
app.include_router(cards_router)
app.include_router(comments_router)
app.include_router(notifications_router)
