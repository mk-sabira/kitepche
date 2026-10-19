from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.book import Book, BookDetail, BookResponse

router = APIRouter()


@router.get("/books", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)):
    return (
        db.query(Book)
        .filter(Book.status == "published")
        .order_by(Book.id)
        .all()
    )


@router.get("/books/{book_id}", response_model=BookDetail)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = (
        db.query(Book)
        .filter(Book.id == book_id, Book.status == "published")
        .first()
    )
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
