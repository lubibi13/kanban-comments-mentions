from typing import Optional
from fastapi import Depends, FastAPI
from fastapi.responses import RedirectResponse
from app.db import init_db
from app.auth import get_optional_user, router as auth_router, web_router as auth_web_router
from app.models import User
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
def root(user: Optional[User] = Depends(get_optional_user)):
    if user:
        return RedirectResponse(url="/boards", status_code=303)
    return RedirectResponse(url="/login", status_code=303)

app.include_router(auth_router)
app.include_router(auth_web_router)
app.include_router(tasks_router)
app.include_router(boards_router)
app.include_router(columns_router)
app.include_router(cards_router)
app.include_router(comments_router)
app.include_router(notifications_router)
