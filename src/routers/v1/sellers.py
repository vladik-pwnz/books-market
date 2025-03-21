import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.configurations import get_async_session
from src.models.sellers import Seller
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller

logger = logging.getLogger(__name__)

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

async def handle_integrity_error(session, email: str):
    """Handles IntegrityError (duplicate email) in create/update operations."""
    await session.rollback()
    logger.warning(f"Email already in use: {email}")
    raise HTTPException(
        status_code=400,
        detail="Email already in use by another seller",
    )

@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(
    seller: IncomingSeller,
    session: DBSession,
):
    try:
        logger.info(f"Attempting to create seller with email: {seller.e_mail}")

        new_seller = Seller(
            first_name=seller.first_name,
            last_name=seller.last_name,
            e_mail=seller.e_mail,
            password=seller.password,  # TODO: hash this password
        )

        session.add(new_seller)
        await session.commit()

        stmt = (
            select(Seller)
            .where(Seller.id == new_seller.id)
            .options(selectinload(Seller.books))
        )
        result = await session.execute(stmt)
        seller_instance = result.scalar_one()

        # Convert to Pydantic model (this now works because the instance is fully loaded)
        return ReturnedSeller.model_validate(seller_instance)

    except IntegrityError:
        await handle_integrity_error(session, seller.e_mail)

    except SQLAlchemyError as e:
        logger.error(f"Database error while creating seller: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )
    except Exception as e:
        logger.error(f"Unexpected error while creating seller: {str(e)}")
        await session.rollback()
        raise


@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    try:
        logger.info(f"Fetching seller with ID: {seller_id}")

        # Use selectinload to eagerly load the relationship
        stmt = (
            select(Seller)
            .where(Seller.id == seller_id)
            .options(selectinload(Seller.books))
        )
        result = await session.execute(stmt)
        seller = result.scalar_one_or_none()

        if not seller:
            logger.warning(f"Seller with ID {seller_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found"
            )

        return seller

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching seller {seller_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )


@sellers_router.get("/", response_model=List[ReturnedSeller], response_model_exclude={"password"})
async def get_all_sellers(session: DBSession):
    try:
        logger.info("Fetching all sellers")
        query = select(Seller).options(selectinload(Seller.books))
        result = await session.execute(query)
        sellers = result.scalars().all()

        logger.info(f"Retrieved {len(sellers)} sellers")
        return sellers

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching all sellers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )


@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, seller_data: IncomingSeller, session: DBSession):
    try:
        logger.info(f"Attempting to update seller with ID: {seller_id}")

        stmt = select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
        result = await session.execute(stmt)
        seller = result.scalar_one_or_none()

        if not seller:
            logger.warning(f"Attempt to update non-existent seller with ID: {seller_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found"
            )

        seller.first_name = seller_data.first_name
        seller.last_name = seller_data.last_name
        seller.e_mail = seller_data.e_mail
        seller.password = seller_data.password  # TODO: hash this password

        try:
            await session.commit()
            await session.refresh(seller)
            logger.info(f"Successfully updated seller with ID: {seller_id}")
            
            # Fetch the updated seller with `selectinload` to avoid lazy loading issues
            stmt = select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
            result = await session.execute(stmt)
            updated_seller = result.scalar_one()

            return updated_seller

        except IntegrityError:
            await handle_integrity_error(session, seller.e_mail)

    except SQLAlchemyError as e:
        logger.error(f"Database error while updating seller {seller_id}: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while updating seller {seller_id}: {str(e)}")
        await session.rollback()
        raise


@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    try:
        logger.info(f"Attempting to delete seller with ID: {seller_id}")

        if seller := await session.get(Seller, seller_id):
            await session.delete(seller)
            await session.commit()

            logger.info(f"Successfully deleted seller with ID: {seller_id}")
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        logger.warning(f"Attempt to delete non-existent seller with ID: {seller_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting seller {seller_id}: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )
