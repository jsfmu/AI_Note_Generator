# AI Flashcard Generator

A modern web application that generates flashcards from PDF documents using AI (Groq).

## Features

- Upload PDF documents
- AI-powered flashcard generation using Groq's Llama 3.3 70B model
- Responsive web interface
- Modern UI/UX design
- Interactive flashcard navigation

## Tech Stack

- Frontend: React + TypeScript + Vite
- Backend: FastAPI (Python)
- AI: Groq API (llama-3.3-70b-versatile model)
- PDF Processing: PyPDF2

## Setup

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- Groq API key (get it from https://console.groq.com/)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on http://localhost:5173

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```

The backend will run on http://localhost:8080

## Environment Variables

Create a `.env` file in the backend directory with:

```
GROQ_API_KEY=your_api_key_here
```

## Usage

1. Start both frontend and backend servers
2. Open your browser to `http://localhost:5173`
3. Upload a PDF document
4. Wait for the AI to generate flashcards
5. Review and study your flashcards using the navigation controls

## API Endpoints

- `POST /api/generate-flashcards`: Generate flashcards from a PDF file
- `GET /api/health`: Health check endpoint

## Error Handling

The application includes comprehensive error handling for:
- Invalid file types
- PDF processing errors
- AI generation errors
- Network issues

## Development

- Frontend hot-reload is enabled
- Backend auto-reload is enabled
- Detailed logging for debugging 