# https://github.com/AkariGroup/akari_chatgpt_bot.git
import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
HUGGINGFACE_ACCESSTOKEN = os.getenv("HUGGINGFACE_ACCESSTOKEN")