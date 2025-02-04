from fastapi import FastAPI, status, Response
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from icecream import ic

# CRUD - Create, Read, Update, Delete

COUNTER = 0  # Каунтер, иметирующий присвоение id в базе данных

# Само приложение fastApi. именно оно запускается сервером и служит точкой входа
# в нем можно указать разные параметры для сваггера и для ручек (эндпоинтов).
app = FastAPI(
    title="Book Library App",
    description="Учебное приложение для MTS Shad",
    version="0.0.1",
    default_response_class=ORJSONResponse,
    responses={404: {"description": "Not found!"}},  # Подключаем быстрый сериализатор
)

# симулируем хранилище данных. Просто сохраняем объекты в память, в словаре.
# {0: {"id": 1, "title": "blabla", ...., "year": 2023}}
fake_storage = {}


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseBook(BaseModel):
    title: str
    author: str
    year: int


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingBook(BaseBook):
    pages: int = Field(
        default=150, alias="count_pages"
    )  # Пример использования тонкой настройки полей. Передачи в них метаинформации.

    @field_validator("year")  # Валидатор, проверяет что дата не слишком древняя
    @staticmethod
    def validate_year(val: int):
        if val < 2020:
            raise PydanticCustomError("Validation error", "Year is too old!")

        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedBook(BaseBook):
    id: int
    pages: int


# Класс для возврата массива объектов "Книга"
class ReturnedAllbooks(BaseModel):
    books: list[ReturnedBook]


# Просто пример ручки и того, как ее можно исключить из схемы сваггера
@app.get("/main", include_in_schema=False)
async def main():
    return "Hello World!"


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
# @app.post("/books/", status_code=status.HTTP_201_CREATED)
@app.post("/books/", response_model=ReturnedBook)  # Прописываем модель ответа
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
@app.get("/books/", response_model=ReturnedAllbooks)
async def get_all_books():
    # Хотим видеть формат
    # books: [{"id": 1, "title": "blabla", ...., "year": 2023},{...}]
    books = list(fake_storage.values())
    return {"books": books}


# Ручка для получения книги по ее ИД
@app.get("/books/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int):
    book = fake_storage.get(book_id)
    if book is not None:
        return book

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления книги
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    deleted_book = fake_storage.pop(book_id, None)
    ic(deleted_book)  # Красивая и информативная замена для print. Полезна при отладке.
    # return Response(status_code=status.HTTP_204_NO_CONTENT)


# Ручка для обновления данных о книге
@app.put("/books/{book_id}", response_model=ReturnedBook)
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
