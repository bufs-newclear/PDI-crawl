import requests
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')


def send_discord_message(message):
    """디스코드 웹훅을 사용하여 메시지를 보냅니다."""
    if not DISCORD_WEBHOOK_URL:
        raise ResourceWarning(
            "환경변수 DISCORD_WEBHOOK_URL 이 정의되지 않았습니다. Discord 웹훅 전송이 불가능합니다."
        )
        return None
    requests.post(DISCORD_WEBHOOK_URL, data={'content': message})
