# AI Travel Itinerary Planner

An AI-powered travel itinerary planner that evolves into a multi-step intelligent agent — not a simple one-shot generator.

## Tech Stack

- **Frontend:** HTML / CSS / JavaScript
- **Backend:** Python (FastAPI)
- **LLM:** Groq API

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   └── llm.py
│   │   ├── __init__.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── .dockerignore
├── Dockerfile
├── .gitignore
└── README.md
```

## Getting Started

### Local Development (Python)

Because FastAPI now serves the static frontend, you only need to run the backend!

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run the server
uvicorn app.main:app --reload
```

Then visit **http://127.0.0.1:8000** in your browser.

### Docker (Production Ready)

To run the entire app (API + Frontend UI) in a single container:

```bash
# Build the image
docker build -t ai-travel-planner .

# Run the container (pass your API key)
docker run -p 8000:8000 -e GROQ_API_KEY="your-groq-key" ai-travel-planner
```

Visit **http://localhost:8000** in your browser.

## Features

- **Blazing Fast**: Streaming LLM responses powered by Groq's super-fast inferencing.
- **Beautiful UI**: Glassmorphism design and responsive UX.
- **Markdown Rendering**: Iterative real-time markdown parsing with `marked.js`.
- **Single Server Architecture**: Zero CORS issues, FastAPI serves both UI and API.

## License

MIT
