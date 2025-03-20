from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from .books import ReturnedBook

__all__ = ["LoginSeller", "IncomingSeller", "ReturnedSeller", "ReturnedAllSellers"]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr


class IncomingSeller(BaseSeller):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, val: str):
        if len(val) < 8:
            raise ValueError("Password is too short!")
        return val


class ReturnedSeller(BaseSeller):
    id: int
    books: Optional[List[ReturnedBook]] = Field(default_factory=list)

    model_config = {"from_attributes": True, "exclude": {"password"}}


class ReturnedAllSellers(BaseModel):
    sellers: List[ReturnedSeller]

    model_config = {"from_attributes": True}


class LoginSeller(BaseModel):
    e_mail: EmailStr
    password: str
