from fastapi import FastAPI
from app.db import init_db
from app.auth import router as auth_router
from app.tasks import router as tasks_router

app = FastAPI(title="Task Starter API", version="0.1.0")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Task Starter API", "docs": "/docs"}

app.include_router(auth_router)
app.include_router(tasks_router)
