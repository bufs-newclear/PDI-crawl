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
        breakfast = daily_meals['breakfast']
        if len(breakfast) == 0 or breakfast[0]['menu'].strip() in ['-', '미운영']:
            send_discord_message(f"{daily_meals['datestring']} 의 조식이 미운영입니다 (\`{breakfast}\`)")

        # lunch
        lunch_names = [meal['menu'].strip() for meal in daily_meals["lunch"]]
        if len(daily_meals['lunch']) == 0 or '미운영' in lunch_names:
            send_discord_message(f"{daily_meals['datestring']} 의 학생식당이 미운영입니다")

        # employee
        if 'employee' not in daily_meals or daily_meals['employee'].strip() in ['-', '미운영']:
            send_discord_message(f"{daily_meals['datestring']} 의 교직원식당이 미운영입니다 (\`{breakfast}\`)")

    # 백엔드 서버로 전송
    send_to_backend(
        meals,
        url=os.environ["BACKEND_URL"],
        username=os.environ['BACKEND_AUTH_USERNAME'],
        password=os.environ['BACKEND_AUTH_PASSWORD'],
    )


if __name__ == "__main__":
    main()
