import json
from collections import Counter, defaultdict


def load(filename):
    with open(f"investigation/data/{filename}", "r", encoding="utf-8") as f:
        return json.load(f)


rentals_data = load("rentals.json")
projects_data = load("projects.json")
listings_data = load("listings.json")


rentals = rentals_data["results"]
projects = projects_data["results"]
listings = listings_data["listings"]


# ============================================================
# Q5 — Total monthly rent in Sohna Road
# ============================================================

sohna_rentals = [
    r for r in rentals
    if str(r.get("locality", "")).strip().lower() == "sohna road"
]

total_monthly_rent = sum(r["price"] for r in sohna_rentals)


print("=" * 70)
print("Q5 — SOHNA ROAD RENT")
print("=" * 70)

print("Sohna Road rental records:", len(sohna_rentals))
print("Total monthly rent:", total_monthly_rent)

print("\nRental prices:")
for r in sohna_rentals:
    print(
        f"{r['listing_id']} | "
        f"{r['price']} | "
        f"{r.get('bedroom')} BHK | "
        f"{r.get('apartment_name')}"
    )


# ============================================================
# Q7 — Costliest project
# ============================================================

costliest = max(
    projects,
    key=lambda p: p.get("price_max", float("-inf"))
)


print("\n" + "=" * 70)
print("Q7 — COSTLIEST PROJECT")
print("=" * 70)

print(json.dumps(costliest, indent=2))


# ============================================================
# Project listing counts
# ============================================================

actual_project_counts = Counter(
    x.get("project_id")
    for x in listings
    if x.get("project_id") is not None
)


mismatches = []

for p in projects:
    project_id = p["project_id"]
    reported = p.get("total_listings")
    actual = actual_project_counts.get(project_id, 0)

    if reported != actual:
        mismatches.append({
            "project_id": project_id,
            "apartment_name": p.get("apartment_name"),
            "locality": p.get("locality"),
            "reported": reported,
            "actual": actual,
        })


# ============================================================
# Q10
# ============================================================

print("\n" + "=" * 70)
print("Q10 — PROJECT LISTING COUNT MISMATCHES")
print("=" * 70)

print("Projects:", len(projects))
print("Mismatches:", len(mismatches))

for x in sorted(mismatches, key=lambda x: x["project_id"]):
    print(
        f"{x['project_id']} | "
        f"{x['apartment_name']} | "
        f"{x['locality']} | "
        f"reported={x['reported']} | "
        f"actual={x['actual']}"
    )


# ============================================================
# Project price unit investigation
# ============================================================

print("\n" + "=" * 70)
print("PROJECT PRICE UNIT CHECK")
print("=" * 70)

# Compare project price_max with maximum listing price for that project.
listing_prices = defaultdict(list)

for x in listings:
    project_id = x.get("project_id")

    if project_id is not None:
        listing_prices[project_id].append(x["price"])


checks = []

for p in projects:
    pid = p["project_id"]

    if pid not in listing_prices:
        continue

    actual_max = max(listing_prices[pid])
    reported_max = p.get("price_max")

    checks.append({
        "project_id": pid,
        "name": p.get("apartment_name"),
        "reported_price_max": reported_max,
        "listing_max": actual_max,
        "ratio": actual_max / reported_max
        if reported_max
        else None,
    })


for x in checks[:30]:
    print(
        f"{x['project_id']} | "
        f"{x['name']} | "
        f"project_max={x['reported_price_max']} | "
        f"listing_max={x['listing_max']} | "
        f"ratio={x['ratio']:.2f}"
    )