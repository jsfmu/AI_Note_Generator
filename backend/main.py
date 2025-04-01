from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import PyPDF2
import groq
import os
from dotenv import load_dotenv
import io
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    logger.error("GROQ_API_KEY not found in environment variables")
    raise ValueError("GROQ_API_KEY not found in environment variables")
client = groq.Groq(api_key=groq_api_key)

class Flashcard(BaseModel):
    question: str
    answer: str

def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        logger.info("Starting PDF text extraction")
        # Create a BytesIO object from the file content
        pdf_file = io.BytesIO(file_content)
        
        # Read the PDF file
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        logger.info(f"Successfully extracted {len(text)} characters from PDF")
        return text
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

def generate_flashcards(text: str) -> List[Flashcard]:
    try:
        logger.info("Starting flashcard generation")
        # Create a prompt for the AI
        prompt = f"""Create flashcards from the following text. Format each flashcard as JSON with 'question' and 'answer' fields. 
        Create concise, clear questions and answers that capture the key concepts.
        
        Text:
        {text}
        
        Format the response as a JSON array of objects, each with 'question' and 'answer' fields.
        Example format:
        [
            {{"question": "What is X?", "answer": "X is..."}},
            {{"question": "How does Y work?", "answer": "Y works by..."}}
        ]
        """
        
        # Generate flashcards using Groq
        logger.info("Sending request to Groq API")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates educational flashcards. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=32768  # Maximum completion tokens for this model
        )
        
        # Parse the response and create Flashcard objects
        response_text = completion.choices[0].message.content
        logger.info(f"Received response from Groq API: {response_text[:100]}...")
        
        # Clean the response text to ensure it's valid JSON
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        # Parse the JSON response
        logger.info("Parsing JSON response")
        flashcards_data = json.loads(response_text)
        
        # Convert to Flashcard objects
        flashcards = [Flashcard(**card) for card in flashcards_data]
        logger.info(f"Successfully generated {len(flashcards)} flashcards")
        return flashcards
        
    except Exception as e:
        logger.error(f"Error generating flashcards: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating flashcards: {str(e)}")

@app.post("/api/generate-flashcards", response_model=List[Flashcard])
async def create_flashcards(pdf_file: UploadFile = File(...)):
    try:
        logger.info(f"Received PDF file: {pdf_file.filename}")
        # Read the file content
        file_content = await pdf_file.read()
        logger.info(f"Read {len(file_content)} bytes from PDF")
        
        # Extract text from PDF
        text = extract_text_from_pdf(file_content)
        
        # Generate flashcards
        flashcards = generate_flashcards(text)
        
        return flashcards
    except Exception as e:
        logger.error(f"Error in create_flashcards endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"} 