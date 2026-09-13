import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_URL = os.environ["IVY_BASE_URL"].rstrip("/")
API_KEY = os.environ["IVY_API_KEY"]
EMAIL = os.environ["IVY_EMAIL"]
PASSWORD = os.environ["IVY_PASSWORD"]

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}


def login():
    r = requests.post(
        f"{BASE_URL}/auth/login",
        headers=HEADERS,
        json={
            "email": EMAIL,
            "password": PASSWORD,
        },
        timeout=30,
    )
    r.raise_for_status()

    data = r.json()
    token = data.get("access_token") or data.get("token")

    if not token:
        raise RuntimeError("Login response did not contain a token")

    return token


def fetch_all(token, endpoint):
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}",
    }

    offset = 0
    limit = 50
    all_records = []
    reported_total = None

    while True:
        r = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            params={
                "limit": limit,
                "offset": offset,
            },
            timeout=30,
        )
        r.raise_for_status()

        data = r.json()

        records = data.get("results", [])

        if reported_total is None:
            reported_total = data.get("total")

        all_records.extend(records)

        print(
            f"{endpoint}: "
            f"offset={offset} "
            f"count={len(records)} "
            f"reported_total={data.get('total')} "
            f"has_more={data.get('has_more')}"
        )

        if not data.get("has_more") or not records:
            break

        offset += len(records)

    print(
        f"\n{endpoint} COMPLETE: "
        f"retrieved={len(all_records)}, "
        f"reported_total={reported_total}\n"
    )

    return {
        "reported_total": reported_total,
        "retrieved_count": len(all_records),
        "results": all_records,
    }


def save(filename, data):
    path = Path("investigation/data") / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {path}")


def main():
    print("Logging in...")
    token = login()
    print("✓ Login successful\n")

    rentals = fetch_all(token, "/v1/rentals")
    save("rentals.json", rentals)

    projects = fetch_all(token, "/v1/projects")
    save("projects.json", projects)


if __name__ == "__main__":
    main()