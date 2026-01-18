from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Book title")
    author_id: int = Field(..., gt=0, description="Author ID")
    genre_id: int = Field(..., gt=0, description="Genre ID")
    year_published: Optional[int] = Field(None, ge=1000, le=datetime.now().year + 10, description="Year published")

    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

class BookCreate(BookBase):
    summary: Optional[str] = Field(None, max_length=10000, description="Book summary")

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author_id: Optional[int] = None
    genre_id: Optional[int] = None
    year_published: Optional[int] = None
    summary: Optional[str] = None

class BookResponse(BaseModel):
    id: int
    title: str
    author_id: int
    genre_id: int
    year_published: int
    summary: Optional[str] = None
    author_name: Optional[str] = None
    genre_name: Optional[str] = None

    class Config:
        from_attributes = True

class AuthorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Author name")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Author name cannot be empty')
        return v.strip().title()  # Capitalize properly

class AuthorResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class GenreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Genre name")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Genre name cannot be empty')
        return v.strip().title()  # Capitalize properly

class GenreResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class AuthorUpdate(BaseModel):
    name: Optional[str] = None

class GenreUpdate(BaseModel):
    name: Optional[str] = None

class ReviewCreate(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID")
    review_text: str = Field(..., min_length=1, max_length=5000, description="Review text")
    rating: float = Field(..., ge=0.0, le=5.0, description="Rating (0.0 to 5.0)")
    
    @validator('review_text')
    def validate_review_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Review text cannot be empty')
        return v.strip()


class ReviewResponse(ReviewCreate):
    id: int
    book_id: int

    class Config:
        from_attributes = True

class GenerateSummaryRequest(BaseModel):
    content: str

class GenerateSummaryResponse(BaseModel):
    summary: str