# Agentic Multimodal Assistant

An AI-powered multimodal assistant backend built with FastAPI. The service accepts text and uploaded files, then routes requests through an agentic workflow that can combine OCR, speech transcription, document handling, search-style tools, and LLM reasoning to produce a structured response.

## What the project does

This backend is designed to handle multimodal inputs such as:

- text prompts
- images
- PDFs and other documents
- audio files

It exposes API endpoints for:

- chat responses with optional file uploads
- streaming chat responses via Server-Sent Events
- upload-only file handling
- health and debug checks

The assistant workflow can use:

- Gemini and Groq as LLM providers
- Whisper for audio transcription
- OCR for extracting text from images and scanned documents
- document comparison, summarization, QA, sentiment, code, PDF, and YouTube-related tools

## Repository Layout

- `backend/` - FastAPI application, services, graph workflow, tools, tests, and sample data
- `docker-compose.yml` - local container setup for the backend and an optional frontend service
- `backend/.env.example` - environment variable template

## Prerequisites

- Python 3.11 or newer
- `pip`
- Docker and Docker Compose if you want a container-based setup

## Environment Setup

The backend reads settings from `backend/.env`. Start by copying the example file:

```bash
cp backend/.env.example backend/.env
```

Then fill in the values you need.

### Environment Variables

| Variable | Purpose |
| --- | --- |
| `APP_NAME` | Display name for the service |
| `ENVIRONMENT` | Runtime environment label such as `development` |
| `DEBUG` | Enables debug mode |
| `API_V1_PREFIX` | Base prefix for versioned API routes |
| `GEMINI_API_KEY` | API key for Gemini access |
| `GROQ_API_KEY` | API key for Groq access |
| `LLM_PROVIDER` | Default provider selection, for example `hybrid` |
| `GEMINI_MODEL` | Gemini model name |
| `GROQ_MODEL` | Groq model name |
| `WHISPER_MODEL` | Whisper model size, for example `small` |
| `OCR_PROVIDER` | OCR engine selection |
| `OCR_TEXT_MIN_CHARS` | Minimum text threshold before OCR is considered complete |
| `OCR_RENDER_ZOOM` | Render scale used for OCR on PDFs/images |
| `MAX_UPLOAD_SIZE_MB` | Maximum upload size in megabytes |

## Local Development Setup

### 1. Create a virtual environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Make sure `backend/.env` exists and contains the values you want to use.

### 4. Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at:

- `http://localhost:8000`
- API base path: `http://localhost:8000/api/v1`

## Docker Setup

If you prefer containers, the project includes a `docker-compose.yml`.

```bash
docker compose up --build
```

This starts the backend on port `8000`.

Note: the compose file also defines a frontend service that expects a `frontend/` directory in the repository. If you are only working with the backend, you can still run the backend service independently or add the frontend later.

## Common Endpoints

- `GET /` - basic status check
- `GET /health` - health check
- `POST /api/v1/upload` - upload files and return metadata
- `POST /api/v1/chat` - run the chat workflow and return a structured response
- `POST /api/v1/chat/stream` - stream chat events as SSE

## Testing

Run the backend tests from the `backend/` directory:

```bash
pytest
```

## Sample Data

The `backend/sample_data/` directory contains example assets you can use for local testing and workflow validation.

## Notes

- If you use OCR or audio workflows heavily, the first request may take longer because models can warm up on startup.
- The application is configured to allow cross-origin requests, which makes it easier to connect a separate frontend during development.
