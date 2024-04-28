from get_meal import BUFSMeals
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Union, Literal

def get_token(url: str, username: str, password: str) -> str:
    """사용자명과 패스워드를 이용하여 인증 토큰을 취득합니다."""
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


def get_meals(url, since_date: Optional[datetime] = None, until_date: Optional[datetime] = None):
    res = requests.get(
        f"{url}/meals/meal/",
        params={
            "sinceDate": since_date.strftime('%Y-%m-%d') if since_date else None,
            "untilDate": until_date.strftime('%Y-%m-%d') if until_date else None
        }
    )

    if not res.ok:
        raise ConnectionError(f"연결에 문제가 발생하였습니다 [{res.status_code}]: {res.reason}")
    else:
        return res.json()

def post_meal(
        url: str,
        date: datetime, 
        name: str, 
        meal_type: Union[Literal['morning'], Literal['lunch'], Literal['employee']], 
        token: str):
    res = requests.post(
        f"{url}/meals/meal/",
        headers={ "Authorization": f"Token {token}" },
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

def send_to_backend(meals: BUFSMeals, url: str, username: str, password: str):
    token = get_token(url, username, password)
    weekly_meals = sorted(meals.weekly_meals, key=lambda x: x["date"])
    
    # 중복 제거를 위해 기존의 리스트를 가져온다
    start = weekly_meals[0]["date"]
    end   = weekly_meals[-1]["date"]
    existing_meals = get_meals(url, since_date=start, until_date=end)
    print(existing_meals)

    if len(existing_meals) != 0:
        raise ValueError(f"해당 날짜에 이미 데이터가 존재합니다.\n{start}-{end}: {existing_meals}")
    
    for daily_meals in weekly_meals:
        date = daily_meals["date"]
        # morning
        morning = daily_meals["breakfast"][0]
        print(morning["menu"])
        post_meal(
            url=url,
            date=date,
            name=morning["menu"],
            meal_type="morning",
            token=token
        )

        # lunch
        for meal in daily_meals["lunch"]:
            if meal["corner"] == "공통찬" or \
               meal["menu"] in ["자장(면/밥) +탕수육", "짬뽕(면/밥) +탕수육", "탕수육"]:
                continue

            print(meal["menu"])
            post_meal(
                url=url,
                date=date,
                name=meal["menu"],
                meal_type="lunch",
                token=token
            )