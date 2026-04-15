import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID: str = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION: str = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
CLAUDE_MODEL_ID: str = os.environ.get("CLAUDE_MODEL_ID", "claude-sonnet-4-6")
MAX_TOKENS: int = 4096
