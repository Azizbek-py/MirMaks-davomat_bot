import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
ADMIN_ID = 5143376517
CHANNEL_ID = os.getenv("CHANNEL_ID")
WEB_APP_URL = os.getenv("WEB_APP_URL")