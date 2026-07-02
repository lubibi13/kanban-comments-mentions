from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select
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

@router.get("/notifications/unread_count")
def unread_count(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    count = session.exec(
        select(func.count()).select_from(Notification).where(Notification.user_id == user.id, Notification.read == False)
    ).one()
    return {"count": count}

@router.patch("/notifications/{notification_id}", response_model=NotificationRead)
def mark_notification_read(notification_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.read = True
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification
