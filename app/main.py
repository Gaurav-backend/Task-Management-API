from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routers import tasks
from app.routers import auth
from app.routers import users
from app.routers import google_auth
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings

app = FastAPI()


app.include_router(tasks.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(google_auth.router)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    same_site="lax",
    https_only=False,  # Local HTTP development only
)

@app.get("/")
def root():
    return {"message": "Task Management API"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {"status": "healthy"}


@app.get("/health/live")
def liveness_check():
    return {"status": "alive"}



@app.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )

    return {"status": "ready"}