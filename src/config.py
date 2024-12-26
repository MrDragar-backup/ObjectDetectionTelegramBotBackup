import os

from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")

log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", None)
log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

