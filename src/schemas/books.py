import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator

__all__ = ["IncomingBook", "ReturnedBook", "ReturnedAllBooks"]


class BaseBook(BaseModel):
    title: str
    author: str
    year: int


class IncomingBook(BaseBook):
    pages: int = Field(default=150, alias="count_pages")
    seller_id: int

    @field_validator("year")
    @classmethod
    def validate_year(cls, year):
        current_year = datetime.datetime.now().year
        if year < 1990 or year > current_year + 1:
            raise ValueError(f"Year must be between 1990 and {current_year + 1}")
        return year


class ReturnedBook(BaseBook):
    id: int
    pages: int
    seller_id: int


class ReturnedAllBooks(BaseModel):
    books: List[ReturnedBook]
