# Для импорта из корневого модуля
# import sys
# sys.path.append("..")
# from main import app

from fastapi import APIRouter, Response, status
from fastapi.responses import ORJSONResponse
from schemas import IncomingBook, ReturnedAllbooks, ReturnedBook
from icecream import ic

books_router = APIRouter(tags=["books"], prefix="/books")

# CRUD - Create, Read, Update, Delete

COUNTER = 0  # Каунтер, иметирующий присвоение id в базе данных

# симулируем хранилище данных. Просто сохраняем объекты в память, в словаре.
# {0: {"id": 1, "title": "blabla", ...., "year": 2023}}
fake_storage = {}


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
# @books_router.post("/books/", status_code=status.HTTP_201_CREATED)
@books_router.post("/", response_model=ReturnedBook)  # Прописываем модель ответа
async def create_book(
    book: IncomingBook,
):  # прописываем модель валидирующую входные данные
    global COUNTER  # счетчик ИД нашей фейковой БД

    # TODO запись в БД
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_book = {
        "id": COUNTER,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "pages": book.pages,
    }

    fake_storage[COUNTER] = new_book
    COUNTER += 1

    return ORJSONResponse(
        {"book": new_book},
        status_code=status.HTTP_201_CREATED,
    )  # Возвращаем объект в формате Json с нужным нам статус-кодом, обработанный нужным сериализатором.


# Ручка, возвращающая все книги
@books_router.get("/", response_model=ReturnedAllbooks)
async def get_all_books():
    # Хотим видеть формат
    # books: [{"id": 1, "title": "blabla", ...., "year": 2023},{...}]
    books = list(fake_storage.values())
    return {"books": books}


# Ручка для получения книги по ее ИД
@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int):
    book = fake_storage.get(book_id)
    if book is not None:
        return book

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления книги
@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    deleted_book = fake_storage.pop(book_id, None)
    ic(deleted_book)  # Красивая и информативная замена для print. Полезна при отладке.
    # return Response(status_code=status.HTTP_204_NO_CONTENT)


# Ручка для обновления данных о книге
@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_book_data: ReturnedBook):
    # book = fake_storage.get(book_id, None)
    # if book:
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его. Заменяет то, что закомментировано выше.
    if _ := fake_storage.get(book_id, None):
        new_book = {
            "id": book_id,
            "title": new_book_data.title,
            "author": new_book_data.author,
            "year": new_book_data.year,
            "pages": new_book_data.pages,
        }

        fake_storage[book_id] = new_book

    return fake_storage[book_id]
