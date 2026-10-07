from app.core.database import SessionLocal
from app.models.book import Book

BOOKS = [
    {"title": "Манас баатыры", "age_group": "10-11", "cover_url": "/books/book-1.jpg"},
    {"title": "Күн жана ай", "age_group": "6-7", "cover_url": "/books/book-2.jpg"},
    {"title": "Мектепке баруу", "age_group": "6-7", "cover_url": "/books/book-3.jpg"},
    {"title": "Жолборс жана кой", "age_group": "8-9", "cover_url": "/books/book-4.jpg"},
    {"title": "Кыргыз элинин жомоктору", "age_group": "8-9", "cover_url": "/books/book-5.jpg"},
    {"title": "Тоолорго саякат", "age_group": "12+", "cover_url": "/books/book-6.jpg"},
]

def seed_books():
    session = SessionLocal()
    try:
        added_count = 0
        for book_data in BOOKS:
            existing = session.query(Book).filter_by(title=book_data["title"]).first()
            if existing:
                continue
            session.add(Book(**book_data))
            added_count += 1
        session.commit()
        print(f"Seeded {added_count} new book(s), skipped {len(BOOKS) - added_count} already present")
    finally:
        session.close()


if __name__ == "__main__":
    seed_books()