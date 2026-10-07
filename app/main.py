from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routers import tasks


app = FastAPI()


app.include_router(tasks.router)


@app.get("/")
def root():
    return {"message": "Task Management API"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {"status": "healthy"}