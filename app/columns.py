from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db import get_session
from app.models import Board, Column, ColumnCreate, ColumnRead, ColumnUpdate, User
from app.auth import get_current_user

router = APIRouter(tags=["columns"])

def get_owned_column(column_id: int, session: Session, user: User) -> Column:
    column = session.get(Column, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    board = session.get(Board, column.board_id)
    if not board or board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Column not found")
    return column

@router.post("/boards/{board_id}/columns", response_model=ColumnRead, status_code=201)
def create_column(board_id: int, payload: ColumnCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    board = session.get(Board, board_id)
    if not board or board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Board not found")
    column = Column(**payload.model_dump(), board_id=board_id)
    session.add(column)
    session.commit()
    session.refresh(column)
    return column

@router.patch("/columns/{column_id}", response_model=ColumnRead)
def update_column(column_id: int, payload: ColumnUpdate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    column = get_owned_column(column_id, session, user)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(column, k, v)
    session.add(column)
    session.commit()
    session.refresh(column)
    return column

@router.delete("/columns/{column_id}", status_code=204)
def delete_column(column_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    column = get_owned_column(column_id, session, user)
    session.delete(column)
    session.commit()
    return None
