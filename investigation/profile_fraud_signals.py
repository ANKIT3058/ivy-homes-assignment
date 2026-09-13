import json
from collections import Counter, defaultdict
from pathlib import Path
from itertools import combinations

DATA = Path(__file__).parent / "data" / "listings.json"


def norm(v):
    return str(v or "").strip().lower()


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    listings = data if isinstance(data, list) else data["listings"]

    print("TOTAL:", len(listings))

    # ---------------------------------------------------------
    # 1. Website distribution
    # ---------------------------------------------------------
    print("\n=== WEBSITE ===")
    websites = Counter(norm(x.get("website")) for x in listings)
    for k, v in websites.most_common():
        print(v, repr(k))

    # ---------------------------------------------------------
    # 2. Listing-ID prefix distribution
    # ---------------------------------------------------------
    print("\n=== LISTING ID PREFIX ===")
    prefixes = Counter(
        x["listing_id"].split("-")[0]
        for x in listings
        if x.get("listing_id")
    )
    for k, v in prefixes.most_common():
        print(v, k)

    # ---------------------------------------------------------
    # 3. Verification / live combinations
    # ---------------------------------------------------------
    print("\n=== LIVE / VERIFIED ===")
    combos = Counter(
        (x.get("is_live"), x.get("is_verified"))
        for x in listings
    )
    for k, v in combos.items():
        print(k, v)

    # ---------------------------------------------------------
    # 4. Records with same phone AND same apartment name
    # ---------------------------------------------------------
    print("\n=== SAME PHONE + SAME APARTMENT NAME ===")
    groups = defaultdict(list)

    for x in listings:
        key = (
            norm(x.get("posted_by_contact")),
            norm(x.get("apartment_name")),
        )
        if key[0] and key[1]:
            groups[key].append(x)

    found = 0
    for key, records in groups.items():
        if len(records) >= 2:
            found += 1
            print(
                "\nPHONE:", key[0],
                "NAME:", key[1],
                "COUNT:", len(records)
            )
            for x in records:
                print(
                    " ",
                    x["listing_id"],
                    "|",
                    x.get("bedroom"), "BHK",
                    "| floor", x.get("floor"),
                    "| price", x.get("price"),
                    "| carpet", x.get("carpet_area"),
                    "| project", x.get("project_id"),
                    "| locality", x.get("locality"),
                )

    print("GROUP COUNT:", found)

    # ---------------------------------------------------------
    # 5. Same phone + same apartment + same BHK
    # ---------------------------------------------------------
    print("\n=== SAME PHONE + NAME + BHK ===")
    groups = defaultdict(list)

    for x in listings:
        key = (
            norm(x.get("posted_by_contact")),
            norm(x.get("apartment_name")),
            x.get("bedroom"),
        )
        if key[0] and key[1]:
            groups[key].append(x)

    found = 0
    for key, records in groups.items():
        if len(records) >= 2:
            found += 1
            print(
                "\nPHONE:", key[0],
                "| NAME:", key[1],
                "| BHK:", key[2],
                "| COUNT:", len(records)
            )
            for x in records:
                print(
                    " ",
                    x["listing_id"],
                    "| price", x.get("price"),
                    "| carpet", x.get("carpet_area"),
                    "| super", x.get("super_built_up_area"),
                    "| floor", x.get("floor"),
                    "| project", x.get("project_id"),
                    "| posted", x.get("posted_at"),
                )

    print("GROUP COUNT:", found)

    # ---------------------------------------------------------
    # 6. Same phone + same BHK + same area
    # ---------------------------------------------------------
    print("\n=== SAME PHONE + BHK + CARPET AREA ===")
    groups = defaultdict(list)

    for x in listings:
        key = (
            norm(x.get("posted_by_contact")),
            x.get("bedroom"),
            x.get("carpet_area"),
        )
        if key[0]:
            groups[key].append(x)

    found = 0
    for key, records in groups.items():
        if len(records) >= 2:
            found += 1
            print(
                "\nPHONE:", key[0],
                "| BHK:", key[1],
                "| AREA:", key[2],
                "| COUNT:", len(records)
            )
            for x in records:
                print(
                    " ",
                    x["listing_id"],
                    "|",
                    x.get("apartment_name"),
                    "| price", x.get("price"),
                    "| project", x.get("project_id"),
                    "| locality", x.get("locality"),
                )

    print("GROUP COUNT:", found)

    # ---------------------------------------------------------
    # 7. Exact duplicates ignoring listing_id / metadata
    # ---------------------------------------------------------
    print("\n=== EXACT PROPERTY DUPLICATES (NO CONTACT/DESCRIPTION) ===")

    fields = [
        "apartment_name",
        "locality",
        "bedroom",
        "bathroom",
        "balcony",
        "floor",
        "total_floors",
        "furnishing",
        "facing_direction",
        "covered_parking",
        "price",
        "carpet_area",
        "super_built_up_area",
        "latitude",
        "longitude",
    ]

    groups = defaultdict(list)

    for x in listings:
        key = tuple(
            norm(x.get(f)) if isinstance(x.get(f), str)
            else x.get(f)
            for f in fields
        )
        groups[key].append(x)

    for records in groups.values():
        if len(records) >= 2:
            print("\nDUPLICATE GROUP")
            for x in records:
                print(
                    " ",
                    x["listing_id"],
                    "| posted", x.get("posted_at"),
                    "| phone", x.get("posted_by_contact"),
                    "| project", x.get("project_id"),
                )

    # ---------------------------------------------------------
    # 8. Suspicious price patterns
    # ---------------------------------------------------------
    print("\n=== ZERO / NEGATIVE PRICE ===")
    for x in listings:
        if (x.get("price") or 0) <= 0:
            print(
                x["listing_id"],
                "| price", x.get("price"),
                "|", x.get("apartment_name"),
                "|", x.get("bedroom"), "BHK",
            )

    # ---------------------------------------------------------
    # 9. Suspicious coordinates
    # ---------------------------------------------------------
    print("\n=== COORDINATE SWAPS / OUTLIERS ===")
    for x in listings:
        lat = x.get("latitude")
        lon = x.get("longitude")

        if lat is None or lon is None:
            continue

        # Gurgaon should roughly be lat 27-29, lon 75-78
        if not (27 <= lat <= 29 and 75 <= lon <= 78):
            print(
                x["listing_id"],
                "| lat", lat,
                "| lon", lon,
                "|", x.get("apartment_name"),
            )


if __name__ == "__main__":
    main()
