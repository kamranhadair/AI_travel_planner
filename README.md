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
│   │   ├── __init__.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── .gitignore
└── README.md
```

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

Open `frontend/index.html` in your browser, or serve it with any static file server.

## License

MIT
