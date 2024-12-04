from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Book
from schemas import BookCreate, BookOut
import crud
from auth import decode_access_token

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get current user from token
def get_current_user(token: str):
    user = decode_access_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@app.get("/books/", response_model=list[BookOut])
def get_books(db: Session = Depends(get_db)):
    return crud.get_books(db)

@app.post("/books/", response_model=BookOut, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db, book)

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    return crud.delete_book(db, book_id)
