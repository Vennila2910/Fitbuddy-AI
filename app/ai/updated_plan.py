from google import genai
from google.genai import types

from ..config import (
    GOOGLE_API_KEY,
    GEMINI_PRO_MODEL
)


def update_workout_plan(
    original_plan,
    feedback,
    user
):

    if not GOOGLE_API_KEY:

        raise RuntimeError(
            "GOOGLE_API_KEY is not configured. "
            "Add your Gemini API key to the .env file."
        )

    prompt = f"""
You are FitBuddy's workout-plan revision assistant.

USER

Goal:
{user.goal}

Intensity:
{user.intensity}

Age:
{user.age}

Weight:
{user.weight} kg


ORIGINAL WORKOUT PLAN

{original_plan}


USER FEEDBACK

{feedback}


TASK

Create a complete revised 7-day workout plan.

Do NOT return only the changed day.

Return all seven days.

Apply the user's feedback where it is
safe and reasonable.

Keep useful parts of the original plan.

Each day must contain:

- Focus
- Warm-up
- Main workout
- Sets/repetitions or duration
- Rest guidance
- Cool-down/recovery

If the user's requested change is unsafe,
replace it with a safer alternative.

Do not diagnose medical conditions.

Do not prescribe medical treatment.

Use plain text headings.

Do not use Markdown tables.
"""

    client = genai.Client(
        api_key=GOOGLE_API_KEY
    )

    response = client.models.generate_content(

        model=GEMINI_PRO_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            temperature=0.5,

            max_output_tokens=3200
        )
    )

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty updated plan."
        )

    return response.text.strip()