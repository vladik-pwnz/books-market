from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy import select
from src.models.books import Book
from src.models.sellers import Seller
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session
from typing import Annotated

books_router = APIRouter(tags=["books"], prefix="/books")

# Dependency injection
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@books_router.post(
    "/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED
)
async def create_book(
    book: IncomingBook,
    session: DBSession,
):
    # Check that the seller exists in the database
    seller = await session.execute(select(Seller).filter(Seller.id == book.seller_id))
    seller = seller.scalar_one_or_none()

    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found"
        )

    new_book = Book(
        title=book.title,
        author=book.author,
        year=book.year,
        pages=book.pages,
        seller_id=book.seller_id,
    )

    session.add(new_book)
    await session.flush()

    return new_book


@books_router.get("/", response_model=ReturnedAllBooks)
async def get_all_books(session: DBSession):
    query = select(Book)  # SELECT * FROM book
    result = await session.execute(query)
    books = result.scalars().all()

    return {"books": books}


@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int, session: DBSession):
    if result := await session.get(Book, book_id):
        return result

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: DBSession):
    deleted_book = await session.get(Book, book_id)

    if deleted_book:
        await session.delete(deleted_book)
        await session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )


@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_book_data: ReturnedBook, session: DBSession):
    if updated_book := await session.get(Book, book_id):
        updated_book.author = new_book_data.author
        updated_book.title = new_book_data.title
        updated_book.year = new_book_data.year
        updated_book.pages = new_book_data.pages

        await session.flush()

        return updated_book

    return Response(status_code=status.HTTP_404_NOT_FOUND)
