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


from groq import Groq, APIError, APIConnectionError, RateLimitError

def build_user_prompt(destination: str, days: int, budget: str) -> str:
    return (
        f"Plan a {days}-day trip to {destination} for a traveller with a "
        f"{budget} budget. Give a detailed day-by-day itinerary."
    )


def generate_itinerary_stream(destination: str, days: int, budget: str):
    try:
        response = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(destination, days, budget)},
            ],
            temperature=0.7,
            max_tokens=1024,
            stream=True,  # Enable streaming
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta is not None:
                yield delta
    except RateLimitError:
        yield "Error: AI Service is currently overloaded. Please try again in a few minutes."
    except APIConnectionError:
        yield "Error: Failed to connect to AI service. Please check your network or try again."
    except APIError as e:
        yield f"Error: AI Service error: {e.message}"
    except Exception as e:
        yield "Error: An unexpected error occurred while generating the itinerary."
