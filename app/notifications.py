from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, func, select
from app.db import get_session
from app.models import Comment, Notification, NotificationRead, User
from app.auth import get_current_user
from app.templates import templates, wants_html

router = APIRouter(tags=["notifications"])

def get_unread_count(session: Session, user: User) -> int:
    return session.exec(
        select(func.count()).select_from(Notification).where(Notification.user_id == user.id, Notification.read == False)
    ).one()

@router.get("/notifications", response_model=List[NotificationRead])
def list_notifications(request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    notifications = session.exec(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.read, Notification.created_at.desc())
    ).all()
    if wants_html(request):
        return templates.TemplateResponse(
            "notifications.html",
            {
                "request": request,
                "notifications": notifications,
                "unread_count": get_unread_count(session, user),
            },
        )
    return notifications

@router.get("/notifications/unread_count")
def unread_count(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return {"count": get_unread_count(session, user)}

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

@router.get("/notifications/{notification_id}/open")
def open_notification(notification_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    comment = session.get(Comment, notification.comment_id) if notification.comment_id else None
    if not comment:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.read = True
    session.add(notification)
    session.commit()
    return RedirectResponse(url=f"/cards/{comment.card_id}", status_code=303)
