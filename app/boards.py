from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.db import get_session
from app.models import Board, BoardCreate, BoardRead, BoardUpdate, Card, Column, ColumnCreate, User
from app.auth import get_current_user
from app.columns import create_column
from app.notifications import get_unread_count
from app.templates import templates, wants_html

router = APIRouter(prefix="/boards", tags=["boards"])

DEFAULT_COLUMN_TITLES = ["To Do", "Doing", "Done"]

@router.get("/", response_model=List[BoardRead])
def list_boards(request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    boards = session.exec(select(Board).where(Board.user_id == user.id).order_by(Board.created_at.desc())).all()
    if wants_html(request):
        return templates.TemplateResponse(
            "boards_index.html",
            {"request": request, "boards": boards, "unread_count": get_unread_count(session, user)},
        )
    return boards

@router.post("/", response_model=BoardRead, status_code=201)
def create_board(payload: BoardCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    board = Board(**payload.model_dump(), user_id=user.id)
    session.add(board)
    session.commit()
    session.refresh(board)
    return board

@router.get("/new")
def new_board_form(request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "board_new.html",
        {"request": request, "unread_count": get_unread_count(session, user)},
    )

@router.post("/new")
def create_board_form(title: str = Form(...), session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    board = create_board(BoardCreate(title=title), session=session, user=user)
    for column_title in DEFAULT_COLUMN_TITLES:
        create_column(board.id, ColumnCreate(title=column_title), session=session, user=user)
    return RedirectResponse(url=f"/boards/{board.id}", status_code=303)

@router.post("/{board_id}/columns/form")
def add_column_form(board_id: int, title: str = Form(...), session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    create_column(board_id, ColumnCreate(title=title), session=session, user=user)
    return RedirectResponse(url=f"/boards/{board_id}", status_code=303)

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
