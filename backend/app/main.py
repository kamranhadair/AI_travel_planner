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

from typing import Optional

class PlanRequest(BaseModel):
    session_id: str = Field(..., example="user-1234")
    destination: str = Field(..., min_length=2, example="Paris")
    days: int = Field(..., ge=1, le=30, example=5)
    budget: Literal["low", "moderate", "high"] = Field(..., example="moderate")
    interests: Optional[str] = Field(None, example="museums, food, history")
    dietary_requirements: Optional[str] = Field(None, example="vegan, nut-free")
    pace: Optional[Literal["relaxed", "moderate", "action-packed"]] = Field(None, example="moderate")

class RefineRequest(BaseModel):
    session_id: str = Field(..., example="user-1234")
    message: str = Field(..., example="Can we do an Italian restaurant instead on day 1?")
    destination: str = Field(..., example="Paris")


# ---------- API Routes ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}

from app.services.llm import generate_itinerary_stream, refine_itinerary_stream

@app.post("/plan")
def generate_plan(request: PlanRequest):
    return StreamingResponse(
        generate_itinerary_stream(
            session_id=request.session_id,
            destination=request.destination,
            days=request.days,
            budget=request.budget,
            interests=request.interests,
            dietary_requirements=request.dietary_requirements,
            pace=request.pace
        ),
        media_type="text/plain"
    )

@app.post("/refine")
def refine_plan(request: RefineRequest):
    return StreamingResponse(
        refine_itinerary_stream(
            session_id=request.session_id, 
            destination=request.destination,
            message=request.message
        ),
        media_type="text/plain"
    )


# ---------- Static Frontend (must be last) ----------
# html=True → serves index.html for any unmatched route (SPA behaviour)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
