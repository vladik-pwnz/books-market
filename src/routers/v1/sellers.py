import logging
from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from src.models.sellers import Seller
from src.schemas import IncomingSeller, ReturnedSeller
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session
from typing import Annotated

logger = logging.getLogger(__name__)

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@sellers_router.post(
    "/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED
)
async def create_seller(
    seller: IncomingSeller,
    session: DBSession,
):
    try:
        logger.info(f"Attempting to create seller with email: {seller.e_mail}")
        
        # Check if email already exists
        existing_seller = await session.execute(
            select(Seller).filter(Seller.e_mail == seller.e_mail)
        )
        if existing_seller.scalar_one_or_none():
            logger.warning(f"Attempt to create seller with existing email: {seller.e_mail}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Seller with this email already exists"
            )
            
        # Validate password (simple length check)
        if len(seller.password) < 8:
            logger.warning(f"Attempt to create seller with invalid password length")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must be at least 8 characters long"
            )

        new_seller = Seller(
            first_name=seller.first_name,
            last_name=seller.last_name,
            e_mail=seller.e_mail,
            password=seller.password,  # TODO: hash this password
        )

        session.add(new_seller)
        await session.commit()
        await session.refresh(new_seller)
        
        logger.info(f"Successfully created seller with ID: {new_seller.id}")
        return new_seller
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating seller: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error while creating seller: {str(e)}")
        await session.rollback()
        raise


@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    try:
        logger.info(f"Fetching seller with ID: {seller_id}")
        if seller := await session.get(Seller, seller_id):
            return seller
        
        logger.warning(f"Seller with ID {seller_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Seller not found"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching seller {seller_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


@sellers_router.get("/", response_model=list[ReturnedSeller])
async def get_all_sellers(session: DBSession):
    try:
        logger.info("Fetching all sellers")
        query = select(Seller)
        result = await session.execute(query)
        sellers = result.scalars().all()
        
        logger.info(f"Retrieved {len(sellers)} sellers")
        return sellers
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching all sellers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, seller_data: IncomingSeller, session: DBSession):
    try:
        logger.info(f"Attempting to update seller with ID: {seller_id}")
        
        if seller := await session.get(Seller, seller_id):
            # Check if new email already exists for a different seller
            if seller.e_mail != seller_data.e_mail:
                logger.info(f"Email change detected from {seller.e_mail} to {seller_data.e_mail}")
                existing_seller = await session.execute(
                    select(Seller).filter(Seller.e_mail == seller_data.e_mail)
                )
                if existing_seller.scalar_one_or_none():
                    logger.warning(f"Attempt to update seller with email already in use: {seller_data.e_mail}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="Email already in use by another seller"
                    )
            
            # Validate password (simple length check)
            if len(seller_data.password) < 8:
                logger.warning(f"Attempt to update seller with invalid password length")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Password must be at least 8 characters long"
                )
                    
            seller.first_name = seller_data.first_name
            seller.last_name = seller_data.last_name
            seller.e_mail = seller_data.e_mail
            seller.password = seller_data.password  # TODO: hash this password
            
            await session.commit()
            await session.refresh(seller)
            
            logger.info(f"Successfully updated seller with ID: {seller_id}")
            return seller
        
        logger.warning(f"Attempt to update non-existent seller with ID: {seller_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Seller not found"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while updating seller {seller_id}: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
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
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Seller not found"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting seller {seller_id}: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )