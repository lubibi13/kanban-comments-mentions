from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from app.db import get_session
from app.models import Board, BoardCreate, BoardRead, BoardUpdate, Card, Column, User
from app.auth import get_current_user
from app.notifications import get_unread_count
from app.templates import templates, wants_html

router = APIRouter(prefix="/boards", tags=["boards"])

@router.get("/", response_model=List[BoardRead])
def list_boards(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return session.exec(select(Board).where(Board.user_id == user.id).order_by(Board.created_at.desc())).all()

@router.post("/", response_model=BoardRead, status_code=201)
def create_board(payload: BoardCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    board = Board(**payload.model_dump(), user_id=user.id)
    session.add(board)
    session.commit()
    session.refresh(board)
    return board

@router.get("/{board_id}", response_model=BoardRead)
def get_board(board_id: int, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    board = session.get(Board, board_id)
    if not board or board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Board not found")
    if wants_html(request):
        columns = session.exec(select(Column).where(Column.board_id == board.id)).all()
        cards_by_column = {
            column.id: session.exec(select(Card).where(Card.column_id == column.id)).all()
            for column in columns
        }
        return templates.TemplateResponse(
            "board.html",
            {
                "request": request,
                "board": board,
                "columns": columns,
                "cards_by_column": cards_by_column,
                "unread_count": get_unread_count(session, user),
            },
        )
    return board

@router.patch("/{board_id}", response_model=BoardRead)
def update_board(board_id: int, payload: BoardUpdate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    board = session.get(Board, board_id)
    if not board or board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Board not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(board, k, v)
    session.add(board)
    session.commit()
    session.refresh(board)
    return board

@router.delete("/{board_id}", status_code=204)
def delete_board(board_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    board = session.get(Board, board_id)
    if not board or board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Board not found")
    session.delete(board)
    session.commit()
    return None
