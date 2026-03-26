import os

from dotenv import load_dotenv

load_dotenv()

SOAR_HOST = os.getenv("SOAR_HOST", "https://localhost")
SOAR_TOKEN = os.getenv("SOAR_TOKEN", "")
SOAR_USER = os.getenv("SOAR_USER", "")
SOAR_PASS = os.getenv("SOAR_PASS", "")
SOAR_VERIFY_SSL = os.getenv("SOAR_VERIFY_SSL", "false").lower() not in (
    "false",
    "0",
    "no",
)
