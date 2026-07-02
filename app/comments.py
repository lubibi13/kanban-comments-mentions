from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db import get_session
from app.models import Comment, CommentCreate, CommentRead, Notification, User
from app.auth import get_current_user
from app.cards import get_owned_card
from app.mentions import find_mentioned_users

router = APIRouter(tags=["comments"])

@router.post("/cards/{card_id}/comments", response_model=CommentRead, status_code=201)
def create_comment(card_id: int, payload: CommentCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    card = get_owned_card(card_id, session, user)
    comment = Comment(card_id=card.id, user_id=user.id, body=payload.body)
    session.add(comment)
    session.commit()
    session.refresh(comment)

    mentioned_users = find_mentioned_users(payload.body, session)
    for mentioned in mentioned_users:
        session.add(Notification(user_id=mentioned.id, type="mention", comment_id=comment.id))
    session.commit()

    return comment
