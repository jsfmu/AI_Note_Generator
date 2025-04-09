from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class FlashcardBase(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    answer: str = Field(..., min_length=1, max_length=1000)
    topic: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[list[str]] = Field(default_factory=list)

class FlashcardCreate(FlashcardBase):
    pass

class Flashcard(FlashcardBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[UUID] = None
    source_document: Optional[str] = None

    class Config:
        from_attributes = True

class FlashcardResponse(BaseModel):
    flashcards: list[Flashcard] 