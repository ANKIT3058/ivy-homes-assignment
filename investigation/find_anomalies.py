import json
from collections import Counter, defaultdict
from pathlib import Path


DATA_FILE = Path(__file__).parent / "data" / "listings.json"


def norm(value):
    return value.strip().lower() if isinstance(value, str) else value


def main():
    with DATA_FILE.open("r", encoding="utf-8") as f:
        listings = json.load(f)["listings"]

    print("=" * 70)
    print("ANOMALY INVESTIGATION")
    print("=" * 70)

    # ------------------------------------------------------------
    # 1. Structural impossibilities
    # ------------------------------------------------------------

    print("\n1. STRUCTURAL IMPOSSIBILITIES")

    checks = {
        "floor > total_floors": [],
        "floor < 0": [],
        "bedroom < 0": [],
        "bathroom < 0": [],
        "price <= 0": [],
        "carpet_area <= 0": [],
        "super_built_up_area <= 0": [],
        "carpet > super_built_up": [],
        "latitude outside India-ish range": [],
        "longitude outside India-ish range": [],
    }

    for x in listings:
        if (
            isinstance(x.get("floor"), (int, float))
            and isinstance(x.get("total_floors"), (int, float))
            and x["floor"] > x["total_floors"]
        ):
            checks["floor > total_floors"].append(x)

        if isinstance(x.get("floor"), (int, float)) and x["floor"] < 0:
            checks["floor < 0"].append(x)

        if isinstance(x.get("bedroom"), (int, float)) and x["bedroom"] < 0:
            checks["bedroom < 0"].append(x)

        if isinstance(x.get("bathroom"), (int, float)) and x["bathroom"] < 0:
            checks["bathroom < 0"].append(x)

        if isinstance(x.get("price"), (int, float)) and x["price"] <= 0:
            checks["price <= 0"].append(x)

        if (
            isinstance(x.get("carpet_area"), (int, float))
            and x["carpet_area"] <= 0
        ):
            checks["carpet_area <= 0"].append(x)

        if (
            isinstance(x.get("super_built_up_area"), (int, float))
            and x["super_built_up_area"] <= 0
        ):
            checks["super_built_up_area <= 0"].append(x)

        if (
            isinstance(x.get("carpet_area"), (int, float))
            and isinstance(x.get("super_built_up_area"), (int, float))
            and x["carpet_area"] > x["super_built_up_area"]
        ):
            checks["carpet > super_built_up"].append(x)

        lat = x.get("latitude")
        lon = x.get("longitude")

        if (
            isinstance(lat, (int, float))
            and not (20 <= lat <= 35)
        ):
            checks["latitude outside India-ish range"].append(x)

        if (
            isinstance(lon, (int, float))
            and not (68 <= lon <= 90)
        ):
            checks["longitude outside India-ish range"].append(x)

    for name, records in checks.items():
        print(f"\n{name}: {len(records)}")

        for x in records[:20]:
            print(
                f"  {x.get('listing_id')} | "
                f"bed={x.get('bedroom')} | "
                f"bath={x.get('bathroom')} | "
                f"floor={x.get('floor')}/{x.get('total_floors')} | "
                f"carpet={x.get('carpet_area')} | "
                f"super={x.get('super_built_up_area')}"
            )

    # ------------------------------------------------------------
    # 2. Phone-number concentration
    # ------------------------------------------------------------

    print("\n2. PHONE NUMBER CONCENTRATION")

    phone_groups = defaultdict(list)

    for x in listings:
        phone = x.get("posted_by_contact")
        if phone:
            phone_groups[phone].append(x)

    repeated_phones = {
        phone: records
        for phone, records in phone_groups.items()
        if len(records) >= 3
    }

    print(f"Phones appearing >= 3 times: {len(repeated_phones)}")

    for phone, records in sorted(
        repeated_phones.items(),
        key=lambda item: len(item[1]),
        reverse=True,
    )[:30]:
        print(
            f"\n  {phone}: {len(records)} listings"
        )

        for x in records[:10]:
            print(
                f"    {x.get('listing_id')} | "
                f"{x.get('apartment_name')} | "
                f"{x.get('locality')} | "
                f"{x.get('price')}"
            )

    # ------------------------------------------------------------
    # 3. Exact duplicate property fingerprints
    # ------------------------------------------------------------

    print("\n3. PROPERTY FINGERPRINTS")

    fingerprints = defaultdict(list)

    for x in listings:
        fingerprint = (
            norm(x.get("apartment_name")),
            norm(x.get("locality")),
            x.get("bedroom"),
            x.get("bathroom"),
            x.get("carpet_area"),
            x.get("super_built_up_area"),
            x.get("latitude"),
            x.get("longitude"),
        )

        fingerprints[fingerprint].append(x)

    repeated_fingerprints = {
        fp: records
        for fp, records in fingerprints.items()
        if len(records) > 1
    }

    print(
        f"Property fingerprints occurring multiple times: "
        f"{len(repeated_fingerprints)}"
    )

    for fp, records in list(repeated_fingerprints.items())[:20]:
        print("\n  Property:")
        print(f"    name={fp[0]}")
        print(f"    locality={fp[1]}")
        print(f"    bedroom={fp[2]}")
        print(f"    carpet={fp[4]}")
        print(f"    coordinates=({fp[6]}, {fp[7]})")

        print("    records:")
        for x in records:
            print(
                f"      {x.get('listing_id')} | "
                f"price={x.get('price')} | "
                f"live={x.get('is_live')} | "
                f"posted_by={x.get('posted_by')}"
            )

    # ------------------------------------------------------------
    # 4. Suspicious descriptions
    # ------------------------------------------------------------

    print("\n4. SUSPICIOUS DESCRIPTION TEXT")

    keywords = [
        "ai assistant",
        "ai coding",
        "submission.json",
        "dataset",
        "license",
        "licence",
        "certified",
        "automated tools",
        "ignore previous",
        "instruction",
    ]

    suspicious = []

    for x in listings:
        description = norm(x.get("description")) or ""

        matched = [
            keyword
            for keyword in keywords
            if keyword in description
        ]

        if matched:
            suspicious.append((x, matched))

    print(f"Descriptions containing investigation-like text: {len(suspicious)}")

    for x, matched in suspicious[:50]:
        print(
            f"  {x.get('listing_id')} | "
            f"matched={matched} | "
            f"{x.get('description')[:180]}"
        )

    # ------------------------------------------------------------
    # 5. Price/area extremes
    # ------------------------------------------------------------

    print("\n5. PRICE PER SQFT EXTREMES")

    priced = []

    for x in listings:
        price = x.get("price")
        area = x.get("carpet_area")

        if (
            isinstance(price, (int, float))
            and isinstance(area, (int, float))
            and area > 0
        ):
            priced.append((price / area, x))

    priced.sort(key=lambda item: item[0])

    print("\nLowest 20:")
    for ppsf, x in priced[:20]:
        print(
            f"  {x.get('listing_id')} | "
            f"{ppsf:.2f}/sqft | "
            f"price={x.get('price')} | "
            f"area={x.get('carpet_area')}"
        )

    print("\nHighest 20:")
    for ppsf, x in priced[-20:][::-1]:
        print(
            f"  {x.get('listing_id')} | "
            f"{ppsf:.2f}/sqft | "
            f"price={x.get('price')} | "
            f"area={x.get('carpet_area')}"
        )


if __name__ == "__main__":
    main()