from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.llm import generate_itinerary_stream

# Resolve frontend directory relative to this file
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

app = FastAPI(
    title="AI Travel Itinerary Planner",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Request schemas ----------

class PlanRequest(BaseModel):
    destination: str = Field(..., min_length=2, example="Paris")
    days: int = Field(..., ge=1, le=30, example=5)
    budget: Literal["low", "moderate", "high"] = Field(..., example="moderate")


# ---------- API Routes ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/plan")
def generate_plan(request: PlanRequest):
    return StreamingResponse(
        generate_itinerary_stream(
            destination=request.destination,
            days=request.days,
            budget=request.budget,
        ),
        media_type="text/plain"
    )


# ---------- Static Frontend (must be last) ----------
# html=True → serves index.html for any unmatched route (SPA behaviour)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
