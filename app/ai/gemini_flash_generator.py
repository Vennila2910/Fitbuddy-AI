from google import genai
from google.genai import types

from ..config import (
    GOOGLE_API_KEY,
    GEMINI_FLASH_MODEL
)


def generate_nutrition_tip_with_flash(user):

    if not GOOGLE_API_KEY:

        raise RuntimeError(
            "GOOGLE_API_KEY is not configured. "
            "Add your Gemini API key to the .env file."
        )

    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.

Give ONE concise nutrition or recovery tip.

User goal:
{user.goal}

Age:
{user.age}

Weight:
{user.weight} kg

Workout intensity:
{user.intensity}

Keep it practical and suitable for
general wellness.

You may mention:

- Hydration
- Balanced meals
- Protein
- Fruits
- Vegetables
- Sleep
- Recovery

Do NOT prescribe medication.

Do NOT recommend extreme dieting.

Do NOT provide unsafe calorie restrictions.

Maximum 120 words.
"""

    client = genai.Client(
        api_key=GOOGLE_API_KEY
    )

    response = client.models.generate_content(

        model=GEMINI_FLASH_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            temperature=0.4,

            max_output_tokens=300
        )
    )

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty nutrition tip."
        )

    return response.text.strip()