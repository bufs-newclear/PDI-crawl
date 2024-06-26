from get_meal import BUFSMeals
import requests
from datetime import datetime
from typing import Optional, Union, Literal
from misc import send_discord_message


def get_token(url: str, username: str, password: str) -> str:
    """사용자명과 패스워드를 이용하여 인증 토큰을 취득합니다."""
    try:
        res = requests.post(
            f"{url}/users/login/",
            json={
                "username": username,
                "password": password
            }
        )

        if not res.ok:
            raise ConnectionError(f"연결에 문제가 발생하였습니다 [{res.status_code}]: {res.reason}")
        else:
            return res.json()['token']
    except Exception as e:
        send_discord_message(f"토큰 취득 중 오류 발생: {str(e)}")
        raise


def get_meals(url, since_date: Optional[datetime] = None, until_date: Optional[datetime] = None):
    try:
        res = requests.get(
            f"{url}/meals/meal/",
            params={
                "sinceDate": since_date.strftime('%Y-%m-%d') if since_date else None,
                "untilDate": until_date.strftime('%Y-%m-%d') if until_date else None
            }
        )

        if not res.ok:
            # 식당정보 연결실패
            raise ConnectionError(f"연결에 문제가 발생하였습니다 [{res.status_code}]: {res.reason}")
        else:
            return res.json()
    except Exception as e:
        send_discord_message(f"식당 정보 조회 중 오류 발생: {str(e)}")
        raise


def post_meal(
        url: str,
        date: datetime,
        name: str,
        meal_type: Union[Literal['morning'], Literal['lunch'], Literal['employee']], 
        token: str):
    try:
        res = requests.post(
            f"{url}/meals/meal/",
            headers={"Authorization": f"Token {token}"},
            json={
                "date": date.strftime("%Y-%m-%d"),
                "name": name,
                "meal_type": meal_type
            }
        )

        if not res.ok:
            raise ConnectionError(f"연결에 문제가 발생하였습니다 [{res.status_code}]: {res.reason}")
        else:
            return res.json()
    except Exception as e:
        send_discord_message(f"식사 등록 중 오류 발생: {str(e)}")
        raise


def send_to_backend(meals: BUFSMeals, url: str, username: str, password: str, force: bool = False):
    token = get_token(url, username, password)
    weekly_meals = sorted(meals.weekly_meals, key=lambda x: x["date"])

    # 중복 제거를 위해 기존의 리스트를 가져온다
    start = weekly_meals[0]["date"]
    end = weekly_meals[-1]["date"]
    existing_meals = get_meals(url, since_date=start, until_date=end)
    print(existing_meals)

    if not force and len(existing_meals) != 0:
        print(f"해당 날짜에 이미 데이터가 존재합니다.\n{start}-{end}: {len(existing_meals)}")
        return

    meal_count = 0
    for daily_meals in weekly_meals:
        date = daily_meals["date"]
        # morning
        for meal in daily_meals["breakfast"]:
            print(meal["menu"])
            post_meal(
                url=url,
                date=date,
                name=meal["menu"],
                meal_type="morning",
                token=token
            )
            meal_count += 1

        # lunch
        for meal in daily_meals["lunch"]:
            if meal["corner"] == "공통찬" or \
               meal["corner"] == "분식" or \
               meal["menu"] in ["자장(면/밥) +탕수육", "짬뽕(면/밥) +탕수육", "탕수육", "옛날돈까스"]:
                continue

            print(meal["menu"])
            post_meal(
                url=url,
                date=date,
                name=meal["menu"],
                meal_type="lunch",
                token=token
            )
            meal_count += 1
        
        # employee
        if 'employee' in daily_meals:
            employee = daily_meals["employee"]
            print(employee)
            post_meal(
                url=url,
                date=date,
                name=employee,
                meal_type="employee",
                token=token
            )
            meal_count += 1
    
    send_discord_message(f"{len(daily_meals)} 일에 대한 식단 {meal_count}건이 추가되었습니다 ({start} - {end})")
