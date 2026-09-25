import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()

GEMINI_PRO_MODEL = os.getenv(
    "GEMINI_PRO_MODEL",
    "gemini-flash-lite-latest"
)

GEMINI_FLASH_MODEL = os.getenv(
    "GEMINI_FLASH_MODEL",
    "gemini-flash-lite-latest"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'fitbuddy.db'}"
)

ADMIN_KEY = os.getenv(
    "ADMIN_KEY",
    "fitbuddy-admin"
)