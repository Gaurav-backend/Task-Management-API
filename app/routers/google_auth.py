import re
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.google_oauth import oauth
from app.core.security import create_access_token
from app.database.database import get_db, settings
from app.models.user import User
from fastapi.responses import RedirectResponse

from app.core.security import (
    create_access_token,
    create_csrf_token,
)

router = APIRouter(
    prefix="/auth/google",
    tags=["Google Authentication"],
)


def generate_username(db: Session, email: str) -> str:
    base = re.sub(
        r"[^a-zA-Z0-9_]",
        "_",
        email.split("@")[0],
    ).strip("_") or "google_user"

    base = base[:40]

    # Add a random suffix and check uniqueness.
    for _ in range(10):
        username = f"{base}_{secrets.token_hex(3)}"

        existing = db.scalar(
            select(User).where(User.username == username)
        )

        if existing is None:
            return username

    raise HTTPException(
        status_code=500,
        detail="Could not generate a unique username",
    )


@router.get("/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
    )


@router.get("/callback", name="google_callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")

    if not userinfo:
        raise HTTPException(
            status_code=401,
            detail="Google identity could not be verified",
        )

    google_sub = userinfo.get("sub")
    email = userinfo.get("email")
    email_verified = userinfo.get("email_verified")

    if not google_sub or not email or email_verified is not True:
        raise HTTPException(
            status_code=401,
            detail="A verified Google identity and email are required",
        )

    # 1. Find an existing Google-linked account.
    user = db.scalar(
        select(User).where(User.google_sub == google_sub)
    )

    if user is None:
        # 2. Avoid automatically linking an existing account
        # based only on matching email addresses.
        existing_email_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_email_user is not None:
            raise HTTPException(
                status_code=409,
                detail=(
                    "An account with this email already exists. "
                    "Sign in using your existing method first. "
                    "Account linking must be completed separately."
                ),
            )

        # 3. Create a new Google-only user.
        user = User(
            email=email,
            username=generate_username(db, email),
            google_sub=google_sub,
            password_hash=None,
        )

        db.add(user)

        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()

            # A concurrent registration may have created the account.
            user = db.scalar(
                select(User).where(User.google_sub == google_sub)
            )

            if user is None:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Could not create the account. "
                        "Please try signing in again."
                    ),
                )

    # 4. Enforce your application's active-user policy.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive",
        )

    # 5. Issue YOUR application's JWT.
    expires_delta = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=expires_delta,
    )

    response = RedirectResponse(
    url="/docs",
    status_code=303,
    )

    max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Local HTTP development only
        samesite="lax",
        max_age=max_age,
        path="/",
    )

    csrf_token = create_csrf_token(access_token)

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=False,  # Local HTTP development only
        samesite="lax",
        max_age=max_age,
        path="/",
    )

    response.headers["Cache-Control"] = "no-store"

    return response