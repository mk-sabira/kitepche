from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.book import Book, BookResponse
from app.core.database import get_db

router = APIRouter()


@router.get("/books", response_model=list[BookResponse])

def get_books(db: Session = Depends(get_db)):
    return db.query(Book).order_by(Book.id).all()