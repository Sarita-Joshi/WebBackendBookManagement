from sqlalchemy.orm import Session
from models import Book, BorrowedBook, History
from schemas import BookCreate

# CRUD operations for Book
def create_book(db: Session, book: BookCreate):
    new_book = Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

def get_books(db: Session):
    return db.query(Book).all()

def get_book_by_id(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()

def delete_book(db: Session, book_id: int):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        db.delete(book)
        db.commit()
    return book

# CRUD operations for Logs
def log_action(db: Session, user_id: int, action: str, details: str = None):
    log_entry = History(user_id=user_id, action=action, details=details)
    db.add(log_entry)
    db.commit()
