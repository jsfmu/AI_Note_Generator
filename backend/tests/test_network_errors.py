import pytest
import aiohttp
import asyncio
from unittest.mock import patch, MagicMock
from ..app.services.flashcard_service import FlashcardService, NetworkError

@pytest.fixture
async def flashcard_service():
    service = FlashcardService()
    yield service
    if service.session:
        await service.session.close()

@pytest.mark.asyncio
async def test_network_connectivity_success(flashcard_service):
    """Test successful network connectivity"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await flashcard_service._test_network_connectivity()
        assert result is True

@pytest.mark.asyncio
async def test_network_connectivity_failure(flashcard_service):
    """Test failed network connectivity"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.side_effect = aiohttp.ClientError("Connection failed")
        
        result = await flashcard_service._test_network_connectivity()
        assert result is False

@pytest.mark.asyncio
async def test_groq_request_retry(flashcard_service):
    """Test retry mechanism for Groq API requests"""
    with patch('groq.Groq.chat.completions.create') as mock_create:
        # Simulate two failures followed by success
        mock_create.side_effect = [
            aiohttp.ClientError("First attempt failed"),
            aiohttp.ClientError("Second attempt failed"),
            MagicMock(choices=[MagicMock(message=MagicMock(content="Success"))])
        ]
        
        result = await flashcard_service._make_groq_request("test prompt")
        assert result == "Success"
        assert mock_create.call_count == 3

@pytest.mark.asyncio
async def test_groq_request_max_retries(flashcard_service):
    """Test maximum retries exceeded"""
    with patch('groq.Groq.chat.completions.create') as mock_create:
        # Simulate continuous failures
        mock_create.side_effect = aiohttp.ClientError("Connection failed")
        
        with pytest.raises(aiohttp.ClientError):
            await flashcard_service._make_groq_request("test prompt")
        assert mock_create.call_count == 3

@pytest.mark.asyncio
async def test_timeout_handling(flashcard_service):
    """Test timeout handling"""
    with patch('groq.Groq.chat.completions.create') as mock_create:
        mock_create.side_effect = asyncio.TimeoutError("Request timed out")
        
        with pytest.raises(asyncio.TimeoutError):
            await flashcard_service._make_groq_request("test prompt")

@pytest.mark.asyncio
async def test_network_error_handling(flashcard_service):
    """Test network error handling"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.side_effect = aiohttp.ClientError("Network error")
        
        result = await flashcard_service._test_network_connectivity()
        assert result is False 