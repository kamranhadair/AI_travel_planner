from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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


# ---------- Routes ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/plan", response_model=PlanResponse)
def generate_plan(request: PlanRequest):
    # Stub — real LLM call replaces this in the next step
    itinerary = (
        f"[STUB] 5-day itinerary for {request.destination} "
        f"({request.days} days, {request.budget} budget) coming soon."
    )
    return PlanResponse(
        destination=request.destination,
        days=request.days,
        budget=request.budget,
        itinerary=itinerary,
    )
