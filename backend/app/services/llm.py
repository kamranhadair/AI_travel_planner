import os
from groq import Groq
from dotenv import load_dotenv
from mem0 import Memory

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])
_memory = Memory()

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are an expert travel planner. "
    "When given a destination, trip duration, and budget level, "
    "you produce a clear, day-by-day itinerary. "
    "Be specific: include morning, afternoon, and evening activities. "
    "Keep the tone friendly and practical."
)


from groq import Groq, APIError, APIConnectionError, RateLimitError

from typing import Optional

def build_user_prompt(
    destination: str, 
    days: int, 
    budget: str,
    interests: Optional[str] = None,
    dietary_requirements: Optional[str] = None,
    pace: Optional[str] = None
) -> str:
    prompt = (
        f"Plan a {days}-day trip to {destination} for a traveller with a "
        f"{budget} budget. "
    )
    
    constraints = []
    if interests:
        constraints.append(f"Focus specifically on these interests: {interests}.")
    if dietary_requirements:
        constraints.append(f"Dietary requirements to strictly follow: {dietary_requirements}.")
    if pace:
        constraints.append(f"The pace of the itinerary should be: {pace}.")
        
    if constraints:
        prompt += " ".join(constraints) + " "
        
    prompt += "Give a detailed day-by-day itinerary with specific venues and timing."
    return prompt


def generate_itinerary_stream(
    session_id: str,
    destination: str, 
    days: int, 
    budget: str,
    interests: Optional[str] = None,
    dietary_requirements: Optional[str] = None,
    pace: Optional[str] = None
):
    try:
        user_prompt = build_user_prompt(destination, days, budget, interests, dietary_requirements, pace)
        
        # Store the initial context into Mem0
        _memory.add(user_prompt, user_id=session_id)
        response = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
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
        yield f"Error: An unexpected error occurred: {str(e)}"

def refine_itinerary_stream(session_id: str, destination: str, message: str):
    try:
        # Retrieve previous memories
        relevant_memories = _memory.search(message, user_id=session_id)
        
        context_str = ""
        if relevant_memories:
            # mem0 returns dicts often containing 'memory' string. Let's extract.
            memory_list = [m.get('memory', m) if isinstance(m, dict) else str(m) for m in relevant_memories]
            context_str = "\n".join(memory_list)
        
        refine_prompt = (
            f"You are modifying the itinerary for {destination}.\n\n"
            f"Here is what you know about the user's previous preferences and plan constraints:\n{context_str}\n\n"
            f"The user has a new request: {message}\n"
            "Respond in a friendly, conversational tone and output the modified itinerary segment or changes required."
        )

        # Store the new request
        _memory.add(message, user_id=session_id)

        response = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": refine_prompt},
            ],
            temperature=0.7,
            max_tokens=1024,
            stream=True,
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta is not None:
                yield delta
    except Exception as e:
        yield f"Error: Could not refine the itinerary due to unexpected error: {str(e)}"
