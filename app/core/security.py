import hashlib
import hmac
import secrets

from fastapi import Request

from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.database.database import settings

from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User

password_hash = PasswordHash.recommended()

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


def create_csrf_token(access_token: str) -> str:
    nonce = secrets.token_urlsafe(32)

    message = f"{access_token}:{nonce}".encode()

    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()

    return f"{nonce}.{signature}"


def verify_csrf_token(
    access_token: str,
    csrf_cookie: str | None,
    csrf_header: str | None,
) -> bool:
    if not csrf_cookie or not csrf_header:
        return False

    if not hmac.compare_digest(csrf_cookie, csrf_header):
        return False

    try:
        nonce, supplied_signature = csrf_cookie.rsplit(".", 1)
    except ValueError:
        return False

    message = f"{access_token}:{nonce}".encode()

    expected_signature = hmac.new(
        settings.SECRET_KEY.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        supplied_signature,
        expected_signature,
    )



def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
):
    using_cookie = credentials is None

    if credentials is not None:
        token = credentials.credentials
    else:
        token = request.cookies.get("access_token")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    # Cookie-authenticated state-changing requests need CSRF protection.
    if using_cookie and request.method not in {
        "GET", "HEAD", "OPTIONS"
    }:
        csrf_valid = verify_csrf_token(
            access_token=token,
            csrf_cookie=request.cookies.get("csrf_token"),
            csrf_header=request.headers.get("X-CSRF-Token"),
        )

        if not csrf_valid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing CSRF token",
            )

    # Keep the remainder of your existing function:
    # jwt.decode(), sub validation, database lookup, and return user.
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    statement = select(User).where(
        User.id == int(user_id)
    )

    user = db.scalar(statement)

    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return current_user