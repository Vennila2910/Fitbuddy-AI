import time

from google import genai
from google.genai import types

from ..config import (
    GOOGLE_API_KEY,
    GEMINI_PRO_MODEL
)


def get_client():

    if not GOOGLE_API_KEY:

        raise RuntimeError(
            "GOOGLE_API_KEY is not configured. "
            "Add your Gemini API key to the .env file."
        )

    return genai.Client(
        api_key=GOOGLE_API_KEY
    )


def generate_workout_gemini(user):

    prompt = f"""
You are FitBuddy, an AI fitness-plan assistant.

Create a safe, practical and personalized
7-day fitness workout plan.

USER INFORMATION

Name: {user.username}

Age: {user.age}

Weight: {user.weight} kg

Fitness Goal: {user.goal}

Preferred Intensity: {user.intensity}


REQUIREMENTS

Create exactly seven day sections.

For every day include:

1. Day
2. Focus
3. Warm-up
4. Main workout
5. Sets/repetitions or duration
6. Rest guidance
7. Cool-down/recovery

Include at least one recovery or rest-focused day.

Keep the plan realistic and easy to understand.

Do not diagnose diseases.

Do not prescribe medical treatment.

Do not recommend dangerous or extreme exercise.

If the requested goal could be unsafe,
keep the recommendation conservative.

Use plain text headings.

Do not use Markdown tables.
"""

    client = get_client()

    for attempt, delay in enumerate((0, 2, 5)):

        if delay:
            time.sleep(delay)

        try:

            response = client.models.generate_content(

                model=GEMINI_PRO_MODEL,

                contents=prompt,

                config=types.GenerateContentConfig(

                    temperature=0.5,

                    max_output_tokens=3000
                )
            )

            break

        except Exception as exc:

            message = str(exc)

            if "503" not in message and "UNAVAILABLE" not in message:
                raise

            if attempt == 2:
                raise

    else:
        raise RuntimeError("Gemini did not return a workout plan.")

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty workout plan."
        )

    return response.text.strip()