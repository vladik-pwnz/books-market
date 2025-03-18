from datetime import datetime, timedelta

from authlib.jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from src.configurations.settings import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
) -> str:
    """
    Create a properly formatted JWT token.
    - Converts `exp` to an integer timestamp.
    - Ensures the token is **UTF-8 encoded**.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": int(expire.timestamp())})

    header = {"alg": ALGORITHM, "typ": "JWT"}
    encoded_jwt = jwt.encode(header, to_encode, SECRET_KEY).decode("utf-8")
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    print(f"Received token: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY)
        print(f"Decoded payload: {payload}")

        if not payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        return payload
    except Exception as e:
        print(f"JWT Decode Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}"
        )
