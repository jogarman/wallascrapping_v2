import logging
import os
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not found. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Telegram notification sent.")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

def notify_completion(count, status="Success"):
    msg = f"Wallascrap Run Completed.\nStatus: {status}\nItems Processed: {count}"
    send_telegram_message(msg)

def notify_error(error_msg):
    msg = f"Wallascrap Error:\n{error_msg}"
    send_telegram_message(msg)
