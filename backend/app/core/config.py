import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY and not TOGETHER_API_KEY:
    raise ValueError("FATAL ERROR: At least one AI service key (GOOGLE_API_KEY or TOGETHER_API_KEY) must be defined in your .env file.")