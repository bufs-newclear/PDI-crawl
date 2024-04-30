#!/usr/bin/env python3
from get_meal import BUFSMeals
from backend import send_to_backend
from dotenv import load_dotenv
import os


def main():
    load_dotenv()
    meals = BUFSMeals()
    send_to_backend(
        meals,
        url = os.environ["BACKEND_URL"],
        username = os.environ['BACKEND_AUTH_USERNAME'],
        password = os.environ['BACKEND_AUTH_PASSWORD'],
    )

    # TODO: 문제 발생 시 report


if __name__ == "__main__":
    main()