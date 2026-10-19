import json
from pathlib import Path

from app.core.database import SessionLocal
from app.models.book import Book

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "books.json"


def seed_books():
    books = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    session = SessionLocal()
    try:
        added = 0
        updated = 0
        for book_data in books:
            existing = session.query(Book).filter_by(title=book_data["title"]).first()
            if existing:
                for field, value in book_data.items():
                    setattr(existing, field, value)
                updated += 1
            else:
                session.add(Book(**book_data))
                added += 1
        session.commit()
        print(f"Seeded: {added} added, {updated} updated")
    finally:
        session.close()


if __name__ == "__main__":
    seed_books()
