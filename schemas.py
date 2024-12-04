from pydantic import BaseModel, Field

# Base schema for book
class BookBase(BaseModel):
    title: str = Field(..., max_length=255, example="1984")
    author: str = Field(..., max_length=255, example="George Orwell")
    publication_year: int = Field(..., gt=0, example=1949)
    genre: str = Field(None, max_length=100, example="Fiction")

# Schemas for Book
class BookCreate(BookBase):
    pass

class BookOut(BookBase):
    id: int
    class Config:
        orm_mode = True

# Schemas for User
class UserBase(BaseModel):
    username: str = Field(..., max_length=50, example="admin")
    role: str = Field(..., example="admin")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="password123")
