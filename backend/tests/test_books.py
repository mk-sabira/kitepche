from app.models.book import Book


def add_book(db_session, **overrides):
    data = {
        "title": "Test book",
        "age_group": "6-7",
        "text": "Some text.",
        "source": "test",
    }
    data.update(overrides)
    book = Book(**data)
    db_session.add(book)
    db_session.commit()
    return book


def test_list_returns_books_in_id_order_without_text(client, db_session):
    add_book(db_session, title="A")
    add_book(db_session, title="B")

    response = client.get("/books")

    assert response.status_code == 200
    data = response.json()
    assert [b["title"] for b in data] == ["A", "B"]
    assert "text" not in data[0]


def test_list_hides_unpublished_books(client, db_session):
    add_book(db_session, title="Visible")
    add_book(db_session, title="Hidden", status="draft")

    titles = [b["title"] for b in client.get("/books").json()]

    assert titles == ["Visible"]


def test_get_book_returns_text_and_source(client, db_session):
    book = add_book(db_session, text="Hello", source="placeholder")

    response = client.get(f"/books/{book.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Test book"
    assert body["text"] == "Hello"
    assert body["source"] == "placeholder"


def test_get_book_without_text_returns_null(client, db_session):
    book = add_book(db_session, text=None, source=None)

    response = client.get(f"/books/{book.id}")

    assert response.status_code == 200
    assert response.json()["text"] is None


def test_get_missing_book_returns_404(client):
    response = client.get("/books/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_get_unpublished_book_returns_404(client, db_session):
    book = add_book(db_session, status="draft")

    response = client.get(f"/books/{book.id}")

    assert response.status_code == 404


def test_non_numeric_id_returns_422(client):
    response = client.get("/books/abc")

    assert response.status_code == 422
