#!/usr/bin/env python3
from get_meal import BUFSMeals
from backend import send_to_backend
from dotenv import load_dotenv
from misc import send_discord_message
import os


def main():
    load_dotenv()
    meals = BUFSMeals()

    # 미운영 검사
    for daily_meals in meals.get_weekly():
        # breakfast
        breakfast = daily_meals['breakfast'][0]['menu'].strip()
        if breakfast in ['-', '미운영']:
            send_discord_message(f"{daily_meals['datestring']} 의 조식이 미운영입니다 (${breakfast})")

        # lunch
        lunch = [meal['menu'].strip() for meal in daily_meals["lunch"]]
        if '미운영' in lunch:
            send_discord_message(f"{daily_meals['datestring']} 의 학생식당이 미운영입니다")

        # employee
        employee = daily_meals['employee'].strip()
        if employee in ['-', '미운영']:
            send_discord_message(f"{daily_meals['datestring']} 의 교직원식당이 미운영입니다 (${breakfast})")

    # 백엔드 서버로 전송
    send_to_backend(
        meals,
        url=os.environ["BACKEND_URL"],
        username=os.environ['BACKEND_AUTH_USERNAME'],
        password=os.environ['BACKEND_AUTH_PASSWORD'],
    )


if __name__ == "__main__":
    main()
