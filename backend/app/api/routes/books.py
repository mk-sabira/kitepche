from fastapi import APIRouter, Depends
from sqlalchemy.orm import SessionLocal

from app.core.database import SessionLocal
from app.models.books import Book, BookResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


@router.get("/books", response_model=list[BookResponse])

def get_books(db: Session = Depends(get_db)):
    return db.query(Book).all()