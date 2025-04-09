import PyPDF2
import io
import json
import groq
from fastapi import HTTPException
from typing import List, Optional
from functools import lru_cache
import logging
import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from ..core.config import get_settings
from ..models.flashcard import Flashcard, FlashcardCreate
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter
from openai import AsyncOpenAI
from PyPDF2 import PdfReader

settings = get_settings()
logger = logging.getLogger(__name__)

class NetworkError(Exception):
    """Custom exception for network-related errors"""
    pass

class FlashcardService:
    def __init__(self):
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 1500
        self.temperature = 0.7
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        # Configure Groq client with timeout and retry settings
        self.groq_client = groq.Groq(
            api_key=settings.GROQ_API_KEY,
            timeout=30.0,  # 30 seconds timeout
            max_retries=3  # Maximum number of retries
        )
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        # Configure aiohttp session with proper timeout and retry settings
        timeout = aiohttp.ClientTimeout(
            total=60,  # Total timeout for the whole request
            connect=10,  # Connection timeout
            sock_read=30  # Socket read timeout
        )
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=aiohttp.TCPConnector(
                limit=100,  # Maximum number of concurrent connections
                ttl_dns_cache=300,  # DNS cache TTL in seconds
                force_close=False,  # Keep connections alive
                enable_cleanup_closed=True,  # Clean up closed connections
                ssl=False  # Disable SSL verification for testing
            )
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text content from PDF bytes."""
        try:
            pdf_file = io.BytesIO(pdf_content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError, NetworkError)),
        reraise=True
    )
    async def _make_groq_request(self, prompt: str) -> str:
        try:
            logger.info("Making request to Groq API")
            
            # Test network connectivity first
            if not await self._test_network_connectivity():
                raise NetworkError("Network connectivity test failed")
            
            completion = await self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates educational flashcards. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=32768
            )
            return completion.choices[0].message.content
        except aiohttp.ClientError as e:
            logger.error(f"Network error while calling Groq API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable. Please try again later."
            )
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout while calling Groq API: {str(e)}")
            raise HTTPException(
                status_code=504,
                detail="Request timed out. Please try again later."
            )
        except RetryError as e:
            logger.error(f"Maximum retries exceeded: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable after multiple retries. Please try again later."
            )
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error processing request. Please try again later."
            )

    async def _test_network_connectivity(self) -> bool:
        """Test network connectivity before making API calls"""
        try:
            if not self.session:
                return False
            
            # Test connection to Groq API
            async with self.session.get("https://api.groq.com/health") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Network connectivity test failed: {str(e)}")
            return False

    async def generate_flashcards(self, text: str) -> List[dict]:
        """Generate flashcards from text using OpenAI API."""
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
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract the flashcards from the response
            content = response.choices[0].message.content
            # Clean up the response to ensure it's valid JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            import json
            flashcards = json.loads(content)
            return flashcards

        except Exception as e:
            logger.error(f"Error generating flashcards: {str(e)}")
            raise 