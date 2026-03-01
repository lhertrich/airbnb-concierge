import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS: str = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD: str = os.environ["GMAIL_APP_PASSWORD"]
AIRBNB_SENDER: str = os.getenv("AIRBNB_SENDER", "messaging@airbnb.com")
