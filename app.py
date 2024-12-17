from fastapi import FastAPI, Depends, HTTPException, Form
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session,  relationship
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

# Constants for JWT and database configuration
SECRET_KEY = "my_secret_key_1234" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120 
DATABASE_URL = "mysql+mysqlconnector://<user>:<pwd>@127.0.0.1:3306/<book_db>"  # MySQL database connection URL

# Database setup
engine = create_engine(DATABASE_URL)  # Create database engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Session
Base = declarative_base()  # Base class for models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app instance
app = FastAPI()

############################## Database models ##############################
class Book(Base):
    """
    Database model for books.
    Fields: id, title, author, publication_year, genre.
    """
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    publication_year = Column(Integer, nullable=False)
    genre = Column(String(100))

class User(Base):
    """
    Database model for users.
    Fields: id, username, hashed_password, role.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(20), default="user")

class BorrowedBook(Base):
    """
    Database model for borrowed books.
    Fields: id, book_id, user_id, due_date, returned.
    """
    __tablename__ = "borrowed_books"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    due_date = Column(String, nullable=False) 
    returned = Column(Boolean, default=False)

    book = relationship("Book", backref="borrowed_books")
    user = relationship("User", backref="borrowed_books")

############################## Pydantic schemas ##############################
class BookSchema(BaseModel):
    # Base schema for book data with validation.
    # Fields: title, author, publication_year, genre.
    id: int | None = None
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    publication_year: int = Field(..., gt=0)
    genre: str = Field(None, max_length=100)
    
class UserRegisterSchema(BaseModel):
    #Schema for user registration. Includes username, password, and role.
    username: str
    password: str
    role: str


############################## Utility functions ##############################
def get_password_hash(password: str):
    """
    returns Hashed password using bcrypt
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """
    Verifies if a plain password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    """
    Creates a JWT access token.
    """
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})  # Add expiration
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    """
    Decodes and validates a JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_db():
    """
    Dependency to get a database session.
    Ensures the session is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
############################## Auth functions ##############################
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieves the current user from the JWT token.
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = db.query(User).filter(User.id == payload["id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def admin_required(user: dict = Depends(get_current_user)):
    """
    Checks if the current user is an admin.
    """
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


############################## user API endpoints ##############################
@app.post("/register/", status_code=201)
def register_user(user: UserRegisterSchema, db: Session = Depends(get_db)):
    """
    Registers a new user.
    """
    print(user.username, user.password)
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"username": new_user.username, "role": new_user.role}

@app.post("/login/")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Authenticates a user and generates an access token.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"id": user.id, "username": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

############################## CRUD API endpoints ##############################
@app.get("/books/", response_model=list[BookSchema])
def get_books(search: str = None, genre: str = None, year = None, db: Session = Depends(get_db)):
    """
    Retrieves all books with optional filters.
    - search: Search keyword for title/author
    - genre: Filter by genre
    - year: Filter by publication year
    returns List of books
    """
    query = db.query(Book)
    if search:
        query = query.filter(Book.title.contains(search) | Book.author.contains(search))
    if genre:
        query = query.filter(Book.genre == genre)
    if year:
        query = query.filter(Book.publication_year == year)
    return query.all()

@app.post("/books/", response_model=BookSchema, status_code=201)
def create_book(book: BookSchema, user: dict = Depends(admin_required), db: Session = Depends(get_db)):
    """
    Creates a new book (admin only).
    returns 201
    """
    new_book = Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

from typing import List

@app.post("/bulk/books/", status_code=201)
def create_books(
    books: List[BookSchema],
    user: dict = Depends(admin_required),
    db: Session = Depends(get_db),
):
    """
    Creates multiple books (admin only).
    returns List of successfully created books and errors for failed ones
    """
    results = {"Total":len(books), "success": 0, "errors": []}

    for book in books:
        try:
            new_book = Book(**book.dict())
            db.add(new_book)
            db.commit()
            db.refresh(new_book)
            results["success"]+=1
            
        except Exception as e:
            # Rollback the session to handle errors cleanly
            db.rollback()
            results["errors"].append({
                "title": book.title,
                "author": book.author,
                "error": str(e)
            })

    return results

@app.put("/books/{book_id}", response_model=BookSchema)
def update_book(book_id: int, book: BookSchema, user: dict = Depends(admin_required), db: Session = Depends(get_db)):
    """
    Updates an existing book by ID (admin only).
    returns Updated book data
    """
    existing_book = db.query(Book).filter(Book.id == book_id).first()
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    for key, value in book.dict(exclude_unset=True).items():
        setattr(existing_book, key, value)
    
    db.commit()
    db.refresh(existing_book)
    return existing_book

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, user: dict = Depends(admin_required), db: Session = Depends(get_db)):
    """
    Deletes a book by ID (admin only).
    returns a Success message
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}

############################## Additional API endpoints ##############################
@app.post("/borrow/{book_id}", status_code=201)
def borrow_book(book_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Borrow a book.
    returns Borrowed book details
    """

    book_exists = db.query(Book).filter(Book.id==book_id).first()
    if not book_exists:
        raise HTTPException(status_code=404, detail="Invalid Book Id")
    # Check if the book is already borrowed
    existing_borrow = db.query(BorrowedBook).filter(
        BorrowedBook.book_id == book_id,
        BorrowedBook.returned == False
    ).first()
    if existing_borrow:
        raise HTTPException(status_code=400, detail="Book is already borrowed")

    # Borrow the book
    borrowed_book = BorrowedBook(
        book_id=book_id,
        user_id=user.id,
        due_date=(datetime.utcnow() + timedelta(days=14)).strftime("%Y-%m-%d"),
        returned=False
    )
    db.add(borrowed_book)
    db.commit()
    db.refresh(borrowed_book)

    return {
        "message": "Book borrowed successfully",
        "borrowed_book": borrowed_book
    }

@app.post("/return/{book_id}", status_code=200)
def return_book(book_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Return a borrowed book.
    """

    # Find the borrowed book record
    borrowed_book = db.query(BorrowedBook).filter(
        BorrowedBook.book_id == book_id,
        BorrowedBook.user_id == user.id,
        BorrowedBook.returned == False
    ).first()
    if not borrowed_book:
        raise HTTPException(status_code=404, detail="Book not found or already returned")

    # Mark the book as returned
    borrowed_book.returned = True
    db.commit()

    return {
        "message": f"Book with ID {book_id} returned successfully"
    }