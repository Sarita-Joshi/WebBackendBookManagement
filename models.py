from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# User Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(20), default="user")  # 'admin' or 'user'

# Book Model
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    publication_year = Column(Integer, nullable=False)
    genre = Column(String(100))

# Borrowed Book Model
class BorrowedBook(Base):
    __tablename__ = "borrowed_books"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    due_date = Column(Date, nullable=False)
    returned = Column(Boolean, default=False)
    book = relationship("Book")
    user = relationship("User")

# History (Logs) Model
class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String, nullable=True)
