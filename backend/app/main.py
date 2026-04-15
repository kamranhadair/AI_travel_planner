from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.services.llm import generate_itinerary

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


# ---------- Request / Response schemas ----------

class PlanRequest(BaseModel):
    destination: str = Field(..., min_length=2, example="Paris")
    days: int = Field(..., ge=1, le=30, example=5)
    budget: str = Field(..., example="moderate")  # low | moderate | high


class PlanResponse(BaseModel):
    destination: str
    days: int
    budget: str
    itinerary: str


# ---------- API Routes ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/plan", response_model=PlanResponse)
def generate_plan(request: PlanRequest):
    try:
        itinerary = generate_itinerary(
            destination=request.destination,
            days=request.days,
            budget=request.budget,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return PlanResponse(
        destination=request.destination,
        days=request.days,
        budget=request.budget,
        itinerary=itinerary,
    )


# ---------- Static Frontend (must be last) ----------
# html=True → serves index.html for any unmatched route (SPA behaviour)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
