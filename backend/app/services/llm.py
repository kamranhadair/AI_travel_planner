import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are an expert travel planner. "
    "When given a destination, trip duration, and budget level, "
    "you produce a clear, day-by-day itinerary. "
    "Be specific: include morning, afternoon, and evening activities. "
    "Keep the tone friendly and practical."
)


def build_user_prompt(destination: str, days: int, budget: str) -> str:
    return (
        f"Plan a {days}-day trip to {destination} for a traveller with a "
        f"{budget} budget. Give a detailed day-by-day itinerary."
    )


def generate_itinerary(destination: str, days: int, budget: str) -> str:
    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(destination, days, budget)},
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content
