import json
from pathlib import Path


DATA_FILE = Path(__file__).parent / "data" / "listings.json"


def main():
    with DATA_FILE.open("r", encoding="utf-8") as f:
        listings = json.load(f)["listings"]

    print("=" * 70)
    print("CORRUPTION CANDIDATE ANALYSIS")
    print("=" * 70)

    # Candidate sets
    floor_bad = {
        x["listing_id"]
        for x in listings
        if x["floor"] > x["total_floors"]
    }

    price_bad = {
        x["listing_id"]
        for x in listings
        if x["price"] <= 0
    }

    area_bad = {
        x["listing_id"]
        for x in listings
        if x["carpet_area"] > x["super_built_up_area"]
    }

    coordinate_bad = {
        x["listing_id"]
        for x in listings
        if not (20 <= x["latitude"] <= 35)
        or not (68 <= x["longitude"] <= 90)
    }

    print("\nCandidate set sizes:")
    print(f"floor > total_floors : {len(floor_bad)}")
    print(f"price <= 0           : {len(price_bad)}")
    print(f"carpet > super       : {len(area_bad)}")
    print(f"bad coordinates      : {len(coordinate_bad)}")

    print("\nOverlaps:")
    print("floor ∩ price:", floor_bad & price_bad)
    print("floor ∩ area:", floor_bad & area_bad)
    print("floor ∩ coordinates:", floor_bad & coordinate_bad)
    print("price ∩ area:", price_bad & area_bad)
    print("price ∩ coordinates:", price_bad & coordinate_bad)
    print("area ∩ coordinates:", area_bad & coordinate_bad)

    all_candidates = (
        floor_bad
        | price_bad
        | area_bad
        | coordinate_bad
    )

    print("\nUnion of all structural candidates:")
    print(f"Count: {len(all_candidates)}")

    # Print every candidate and every violated invariant.
    by_id = {x["listing_id"]: x for x in listings}

    for listing_id in sorted(all_candidates):
        x = by_id[listing_id]

        violations = []

        if x["floor"] > x["total_floors"]:
            violations.append("floor>total_floors")

        if x["price"] <= 0:
            violations.append("price<=0")

        if x["carpet_area"] > x["super_built_up_area"]:
            violations.append("carpet>super")

        if not (20 <= x["latitude"] <= 35):
            violations.append("bad_latitude")

        if not (68 <= x["longitude"] <= 90):
            violations.append("bad_longitude")

        print(
            f"{listing_id} | "
            f"violations={','.join(violations)} | "
            f"bed={x['bedroom']} | "
            f"price={x['price']} | "
            f"carpet={x['carpet_area']} | "
            f"super={x['super_built_up_area']} | "
            f"floor={x['floor']}/{x['total_floors']} | "
            f"lat={x['latitude']} | "
            f"lon={x['longitude']} | "
            f"live={x['is_live']}"
        )

    # ------------------------------------------------------------
    # Q4 candidate intersection
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("LIKELY Q4 CANDIDATES")
    print("=" * 70)

    # Records violating at least TWO independent invariants
    multi_bad = []

    for listing_id in all_candidates:
        x = by_id[listing_id]

        violations = 0

        if x["floor"] > x["total_floors"]:
            violations += 1

        if x["price"] <= 0:
            violations += 1

        if x["carpet_area"] > x["super_built_up_area"]:
            violations += 1

        if not (20 <= x["latitude"] <= 35):
            violations += 1

        if not (68 <= x["longitude"] <= 90):
            violations += 1

        if violations >= 2:
            multi_bad.append(listing_id)

    print(
        "Records violating >=2 independent invariants:",
        len(multi_bad)
    )

    print("\nIDs:")
    for listing_id in sorted(multi_bad):
        print(" ", listing_id)


if __name__ == "__main__":
    main()