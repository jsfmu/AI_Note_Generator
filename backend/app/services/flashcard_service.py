from typing import List, Dict
import PyPDF2
import io
import json
import logging
from app.core.config import settings
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class FlashcardService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 1500
        self.temperature = 0.7

    async def extract_text_from_pdf(self, file_content: bytes) -> str:
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    async def generate_flashcards(self, text: str) -> List[Dict[str, str]]:
        try:
            prompt = f"""
            Create a list of flashcards from the following text. Each flashcard should have a clear question and a concise answer.
            Format each flashcard as a JSON object with 'question' and 'answer' fields.
            Return only the JSON array of flashcards, nothing else.

            Text:
            {text}
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates educational flashcards."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            content = response.choices[0].message.content
            
            # Clean up the response to ensure it's valid JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error generating flashcards: {str(e)}")
            raise 