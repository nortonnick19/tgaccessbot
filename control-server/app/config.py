import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

ENV_FILE = BASE_DIR / ".env"


load_dotenv(
    ENV_FILE
)


BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


ADMIN_IDS = [
    int(x)
    for x in os.getenv(
        "ADMIN_IDS",
        ""
    ).split(",")
    if x.strip()
]


if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN missing"
    )


if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL missing"
    )
