from sqlalchemy import String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel


class Seller(BaseModel):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    e_mail: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    books: Mapped[list["Book"]] = relationship("Book", back_populates="seller")
