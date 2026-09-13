import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("IVY_BASE_URL")
API_KEY = os.getenv("IVY_API_KEY")
EMAIL = os.getenv("IVY_EMAIL")
PASSWORD = os.getenv("IVY_PASSWORD")

if not BASE_URL or not API_KEY or not EMAIL or not PASSWORD:
    raise RuntimeError(
        "Missing IVY_BASE_URL, IVY_API_KEY, IVY_EMAIL, or IVY_PASSWORD in .env"
    )

DATA_DIR = Path(__file__).parent / "data"
LISTINGS_FILE = DATA_DIR / "listings.json"

def login():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "email": EMAIL,
            "password": PASSWORD,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()
    token = data.get("access_token") or data.get("token")

    if not token:
        raise RuntimeError(f"Login succeeded but no token was found: {data}")

    print("✓ Login successful")
    return token


def fetch_all_listings(token):
    headers = {
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {token}",
    }

    limit = 200
    offset = 0
    all_listings = []
    expected_total = None

    while True:
        response = requests.get(
            f"{BASE_URL}/v1/listings",
            headers=headers,
            params={
                "limit": limit,
                "offset": offset,
            },
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])

        if expected_total is None:
            expected_total = data.get("total")
            print(f"API reports total listings: {expected_total}")

        all_listings.extend(results)

        print(
            f"Fetched {len(results):3d} records "
            f"(offset={offset}, total downloaded={len(all_listings)})"
        )

        if not data.get("has_more"):
            break

        if not results:
            raise RuntimeError(
                "API says has_more=true but returned no results."
            )

        offset += len(results)

    if expected_total is not None and len(all_listings) != expected_total:
        print(
            f"WARNING: API reported total={expected_total}, "
            f"but pagination returned {len(all_listings)} records."
        )

    return all_listings


def save_listings(listings):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "source": f"{BASE_URL}/v1/listings",
        "count": len(listings),
        "listings": listings,
    }

    with LISTINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print(f"✓ Saved {len(listings)} listings to {LISTINGS_FILE}")


def main():
    token = login()
    listings = fetch_all_listings(token)
    save_listings(listings)


if __name__ == "__main__":
    main()