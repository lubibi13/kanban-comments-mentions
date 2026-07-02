from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from app.db import get_session
from app.models import Board, Card, CardCreate, CardRead, CardUpdate, Column, Comment, User
from app.auth import get_current_user
from app.columns import get_owned_column
from app.notifications import get_unread_count
from app.templates import templates

router = APIRouter(tags=["cards"])

def get_owned_card(card_id: int, session: Session, user: User) -> Card:
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    column = session.get(Column, card.column_id)
    board = session.get(Board, column.board_id) if column else None
    if not board or board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@router.post("/columns/{column_id}/cards", response_model=CardRead, status_code=201)
def create_card(column_id: int, payload: CardCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    column = get_owned_column(column_id, session, user)
    card = Card(**payload.model_dump(), column_id=column.id)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card

@router.get("/cards/{card_id}")
def card_detail(card_id: int, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    card = get_owned_card(card_id, session, user)
    column = session.get(Column, card.column_id)
    other_columns = session.exec(
        select(Column).where(Column.board_id == column.board_id, Column.id != column.id)
    ).all()
    comments = session.exec(
        select(Comment).where(Comment.card_id == card.id).order_by(Comment.created_at)
    ).all()
    authors = {comment.user_id: session.get(User, comment.user_id) for comment in comments}
    return templates.TemplateResponse(
        "card.html",
        {
            "request": request,
            "card": card,
            "column": column,
            "other_columns": other_columns,
            "comments": comments,
            "authors": authors,
            "unread_count": get_unread_count(session, user),
        },
    )

@router.patch("/cards/{card_id}", response_model=CardRead)
def update_card(card_id: int, payload: CardUpdate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    card = get_owned_card(card_id, session, user)
    data = payload.model_dump(exclude_unset=True)
    if "column_id" in data:
        get_owned_column(data["column_id"], session, user)
    for k, v in data.items():
        setattr(card, k, v)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card

@router.delete("/cards/{card_id}", status_code=204)
def delete_card(card_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    card = get_owned_card(card_id, session, user)
    session.delete(card)
    session.commit()
    return None
