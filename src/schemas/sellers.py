from pydantic import BaseModel, EmailStr, Field, field_validator, validator
from pydantic import ValidationError
from typing import List, Optional
from .books import ReturnedAllBooks, ReturnedBook

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedAllSellers"]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr
    password: str


class IncomingSeller(BaseSeller):
    @field_validator("password")
    @staticmethod
    def validate_password(val: str):
        if len(val) < 8:
            raise ValueError("Password is too short!")
        return val


class ReturnedSeller(BaseSeller):
    id: int
    books: Optional[List[ReturnedBook]] = []

    model_config = {
        'from_attributes': True,
        'exclude': {'password'}
    }


class ReturnedAllSellers(BaseModel):
    sellers: List[ReturnedSeller]
    
    model_config = {
        'from_attributes': True
    }
