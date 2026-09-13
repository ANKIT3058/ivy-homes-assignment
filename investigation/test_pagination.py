import os

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_URL = os.getenv("IVY_BASE_URL")
API_KEY = os.getenv("IVY_API_KEY")
EMAIL = os.getenv("IVY_EMAIL")
PASSWORD = os.getenv("IVY_PASSWORD")


def login():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        headers={"X-API-Key": API_KEY},
        json={
            "email": EMAIL,
            "password": PASSWORD,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("access_token") or data.get("token")


def fetch(offset):
    token = login()

    response = requests.get(
        f"{BASE_URL}/v1/listings",
        headers={
            "X-API-Key": API_KEY,
            "Authorization": f"Bearer {token}",
        },
        params={
            "limit": 200,
            "offset": offset,
        },
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


def main():
    for offset in [3300, 3350, 3400, 3450, 3500, 3550]:
        data = fetch(offset)

        print(
            f"offset={offset:4d} "
            f"count={data.get('count'):2d} "
            f"returned={len(data.get('results', [])):2d} "
            f"total={data.get('total')} "
            f"has_more={data.get('has_more')}"
        )


if __name__ == "__main__":
    main()