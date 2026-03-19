from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate


router = APIRouter()


@router.post('/', response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_note = Note(
        title=note_data.title,
        content=note_data.content,
        is_pinned=note_data.is_pinned,
        color=note_data.color,
        owner_id=current_user.id,
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@router.get('/', response_model=List[NoteResponse])
def get_all_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    pinned_only: bool = Query(default=False),
):
    query = db.query(Note).filter(Note.owner_id == current_user.id)

    if pinned_only:
        query = query.filter(Note.is_pinned.is_(True))

    if search:
        query = query.filter(Note.title.ilike(f'%{search}%'))

    return (
        query.order_by(Note.is_pinned.desc(), Note.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get('/{note_id}', response_model=NoteResponse)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail='Note not found')

    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not allowed to access this note')

    return note


@router.put('/{note_id}', response_model=NoteResponse)
def update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail='Note not found')

    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not allowed to update this note')

    update_data = note_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)
    return note


@router.delete('/{note_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail='Note not found')

    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not allowed to delete this note')

    db.delete(note)
    db.commit()


@router.patch('/{note_id}/pin', response_model=NoteResponse)
def toggle_pin(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail='Note not found')

    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not allowed to pin this note')

    note.is_pinned = not note.is_pinned
    db.commit()
    db.refresh(note)
    return note
