from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import logging
from ...services.flashcard_service import FlashcardService
from ...models.flashcard import Flashcard, FlashcardResponse

router = APIRouter()
logger = logging.getLogger(__name__)
flashcard_service = FlashcardService()

@router.post("/generate", response_model=FlashcardResponse)
async def create_flashcards(file: UploadFile = File(...)):
    try:
        # Validate file type
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Read file content
        file_content = await file.read()
        
        # Extract text from PDF
        text = flashcard_service.extract_text_from_pdf(file_content)
        
        if not text:
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")
        
        # Generate flashcards
        flashcards_data = await flashcard_service.generate_flashcards(text)
        
        if not flashcards_data:
            raise HTTPException(status_code=400, detail="No flashcards could be generated")
        
        # Convert to Flashcard objects
        flashcards = [Flashcard(**card) for card in flashcards_data]
        
        return FlashcardResponse(flashcards=flashcards)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy"} 