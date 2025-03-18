from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations import get_async_session
from src.models.sellers import Seller
from src.schemas import (IncomingSeller, LoginSeller, ReturnedAllSellers,
                         ReturnedSeller)
from src.utils.auth import (create_access_token, get_current_user,
                            verify_password)

auth_router = APIRouter(tags=["auth"], prefix="/auth")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@auth_router.post("/token")
async def login_for_access_token(seller: LoginSeller, session: DBSession):
    """Authenticate seller and return JWT token."""
    result = await session.execute(
        select(Seller).filter(Seller.e_mail == seller.e_mail)
    )
    seller_from_db = result.scalar_one_or_none()

    if not seller_from_db or not verify_password(
        seller.password, seller_from_db.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    to_encode = {"sub": seller_from_db.e_mail}
    access_token = create_access_token(to_encode)

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/secure-endpoint")
async def get_secure_data(current_user: dict = Depends(get_current_user)):
    """Secure endpoint requiring authentication."""
    return {"message": "You have access to this endpoint", "user": current_user}
