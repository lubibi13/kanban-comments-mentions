from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.db import get_session
from app.models import Notification, NotificationRead, User
from app.auth import get_current_user

router = APIRouter(tags=["notifications"])

@router.get("/notifications", response_model=List[NotificationRead])
def list_notifications(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return session.exec(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.read, Notification.created_at.desc())
    ).all()
