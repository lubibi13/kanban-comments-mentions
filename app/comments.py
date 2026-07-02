from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from app.db import get_session
from app.models import Card, Comment, CommentCreate, CommentRead, Notification, User
from app.auth import get_current_user
from app.cards import get_owned_card
from app.mentions import find_mentioned_users

router = APIRouter(tags=["comments"])

def _create_comment(card: Card, body: str, user: User, session: Session) -> Comment:
    comment = Comment(card_id=card.id, user_id=user.id, body=body)
    session.add(comment)
    session.commit()
    session.refresh(comment)

    mentioned_users = find_mentioned_users(body, session)
    for mentioned in mentioned_users:
        session.add(Notification(user_id=mentioned.id, type="mention", comment_id=comment.id))
    session.commit()

    return comment

@router.post("/cards/{card_id}/comments", response_model=CommentRead, status_code=201)
def create_comment(card_id: int, payload: CommentCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    card = get_owned_card(card_id, session, user)
    return _create_comment(card, payload.body, user, session)

@router.post("/cards/{card_id}/comments/form")
def create_comment_form(card_id: int, body: str = Form(...), session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    card = get_owned_card(card_id, session, user)
    _create_comment(card, body, user, session)
    return RedirectResponse(url=f"/cards/{card_id}", status_code=303)
