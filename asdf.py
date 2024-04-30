import requests


DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1234822736216457266/ykP_jiHklZfBh8dvC2H79X-nrt2Vl8_3Ai82AokjWGSb8p7YImzkB-YFbMRMrBJXK1VA"

def send_message(message):
    requests.post(DISCORD_WEBHOOK_URL, data=message)

message = {'content':'오류가 발생하였습니다.'}
requests.post(DISCORD_WEBHOOK_URL, data=message)
