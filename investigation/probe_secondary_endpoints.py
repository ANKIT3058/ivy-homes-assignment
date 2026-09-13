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
    response = requests.post(
        f"{BASE_URL}/auth/login",
        headers=HEADERS,
        json={
            "email": EMAIL,
            "password": PASSWORD,
        },
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    # The API uses a bearer token after login.
    token = data.get("access_token") or data.get("token")

    if not token:
        raise RuntimeError(
            f"Could not find token in login response: {data}"
        )

    return token


def get(token, path, params=None):
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(
        f"{BASE_URL}{path}",
        headers=headers,
        params=params,
        timeout=30,
    )

    print(
        f"GET {path}"
        f"{'?' + str(params) if params else ''}"
        f" -> {response.status_code}"
    )

    response.raise_for_status()
    return response.json()


def save(name, data):
    path = Path("investigation/data") / name
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved: {path}")


def inspect_pagination(token, endpoint):
    print("\n" + "=" * 70)
    print(f"PAGINATION TEST: {endpoint}")
    print("=" * 70)

    first = get(token, endpoint, {"limit": 5})
    second_page = get(token, endpoint, {"limit": 5, "page": 2})
    offset_five = get(token, endpoint, {"limit": 5, "offset": 5})

    print("\nFirst request:")
    print(json.dumps(first, indent=2)[:3000])

    print("\npage=2:")
    print(json.dumps(second_page, indent=2)[:3000])

    print("\noffset=5:")
    print(json.dumps(offset_five, indent=2)[:3000])


def main():
    print("Logging in...")
    token = login()
    print("✓ Login successful")

    # Test whether rentals/projects follow their documented page pagination.
    inspect_pagination(token, "/v1/rentals")
    inspect_pagination(token, "/v1/projects")

    # Fetch analytics.
    print("\n" + "=" * 70)
    print("ANALYTICS")
    print("=" * 70)

    analytics = get(token, "/v1/analytics/summary")
    print(json.dumps(analytics, indent=2))

    save("analytics_summary.json", analytics)


if __name__ == "__main__":
    main()