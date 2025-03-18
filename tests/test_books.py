import uuid

import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller


@pytest_asyncio.fixture
async def create_seller(db_session):
    e_mail = f"testuser+{uuid.uuid4()}@example.com"
    seller = Seller(
        first_name="John", last_name="Doe", e_mail=e_mail, password="password123"
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)
    return seller


@pytest.mark.asyncio
async def test_create_book(async_client, db_session, create_seller):
    seller = create_seller

    assert seller.id is not None, "Seller id is None"

    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 2025,
        "seller_id": seller.id,
    }
    response = await async_client.post("/api/v1/books/", json=data)
    assert response.status_code == status.HTTP_201_CREATED
    result_data = response.json()

    print(f"Result data: {result_data}")

    resp_book_id = result_data.pop("id", None)
    assert resp_book_id, "Book id not returned from endpoint"

    expected_data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 2025,
        "seller_id": seller.id,
    }

    assert result_data == expected_data, (
        f"Expected {expected_data}, but got {result_data}"
    )


@pytest.mark.asyncio
async def test_create_book_with_old_year(async_client, db_session, create_seller):
    seller = create_seller

    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 1986,
        "seller_id": seller.id,
    }
    response = await async_client.post("/api/v1/books/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_books(db_session, async_client, create_seller):
    seller = create_seller

    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2001,
        pages=104,
        seller_id=seller.id,
    )
    book_2 = Book(
        author="Lermontov", title="Mziri", year=1997, pages=104, seller_id=seller.id
    )
    db_session.add_all([book, book_2])
    await db_session.commit()
    await db_session.refresh(book)
    await db_session.refresh(book_2)

    response = await async_client.get("/api/v1/books/")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json["books"]) == 2

    expected_books = [
        {
            "title": "Eugeny Onegin",
            "author": "Pushkin",
            "year": 2001,
            "id": book.id,
            "pages": 104,
            "seller_id": seller.id,
        },
        {
            "title": "Mziri",
            "author": "Lermontov",
            "year": 1997,
            "id": book_2.id,
            "pages": 104,
            "seller_id": seller.id,
        },
    ]
    response_books = sorted(response_json["books"], key=lambda x: x["id"])
    expected_books = sorted(expected_books, key=lambda x: x["id"])
    assert response_books == expected_books


@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client, create_seller):
    seller = create_seller

    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2001,
        pages=104,
        seller_id=seller.id,
    )
    book_2 = Book(
        author="Lermontov", title="Mziri", year=1997, pages=104, seller_id=seller.id
    )
    db_session.add_all([book, book_2])
    await db_session.commit()
    await db_session.refresh(book)
    await db_session.refresh(book_2)

    response = await async_client.get(f"/api/v1/books/{book.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "pages": 104,
        "id": book.id,
        "seller_id": seller.id,
    }


@pytest.mark.asyncio
async def test_update_book(db_session, async_client, create_seller):
    seller = create_seller

    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2001,
        pages=104,
        seller_id=seller.id,
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={
            "title": "Mziri",
            "author": "Lermontov",
            "pages": 100,
            "year": 2007,
            "id": book.id,
            "seller_id": seller.id,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    res = await db_session.get(Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.pages == 100
    assert res.year == 2007
    assert res.id == book.id


@pytest.mark.asyncio
async def test_delete_book(db_session, async_client, create_seller):
    seller = create_seller

    book = Book(
        author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    response = await async_client.delete(f"/api/v1/books/{book.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    all_books = await db_session.execute(select(Book))
    res = all_books.scalars().all()
    assert len(res) == 0, f"Book was not deleted. Remaining books: {res}"


@pytest.mark.asyncio
async def test_delete_book_with_invalid_book_id(
    db_session, async_client, create_seller
):
    seller = create_seller

    book = Book(
        author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    invalid_book_id = book.id + 1  # wrong ID
    response = await async_client.delete(f"/api/v1/books/{invalid_book_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND, (
        f"Expected 404, got {response.status_code}"
    )
