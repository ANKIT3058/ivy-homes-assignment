import json
import re
from collections import defaultdict, Counter
from pathlib import Path

DATA = Path(__file__).parent / "data" / "listings.json"


def norm(value):
    if value is None:
        return ""
    value = str(value).lower().strip()
    value = re.sub(r"\s+", " ", value)
    return value


def load_listings():
    data = json.loads(DATA.read_text(encoding="utf-8"))

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        # Common API/export wrapper
        for key in ("results", "listings", "data"):
            if isinstance(data.get(key), list):
                return data[key]

    raise ValueError(
        f"Unexpected listings.json structure: {type(data).__name__}"
    )


def main():
    listings = load_listings()

    print("=" * 70)
    print("FAKE LISTING INVESTIGATION")
    print("=" * 70)
    print(f"Total records: {len(listings)}")

    # ------------------------------------------------------------
    # 1. Exact property-content duplicates
    # ------------------------------------------------------------
    # If two records have essentially identical property facts but
    # different listing IDs, they may represent the same underlying
    # property/listing being duplicated.
    #
    # We deliberately exclude poster/contact/description because those
    # can change independently.
    # ------------------------------------------------------------

    groups = defaultdict(list)

    for x in listings:
        key = (
            norm(x.get("apartment_name")),
            norm(x.get("locality")),
            x.get("bedroom"),
            x.get("bathroom"),
            x.get("balcony"),
            x.get("floor"),
            x.get("total_floors"),
            norm(x.get("furnishing")),
            norm(x.get("facing_direction")),
            x.get("covered_parking"),
            x.get("price"),
            x.get("carpet_area"),
            x.get("super_built_up_area"),
        )
        groups[key].append(x)

    duplicate_groups = [
        records for records in groups.values()
        if len(records) > 1
    ]

    print("\n" + "=" * 70)
    print("1. IDENTICAL PROPERTY-ATTRIBUTE GROUPS")
    print("=" * 70)
    print(f"Groups: {len(duplicate_groups)}")
    print(f"Records involved: {sum(len(g) for g in duplicate_groups)}")

    for group in duplicate_groups:
        print("\nGROUP")
        for x in group:
            print(
                f"  {x['listing_id']} | "
                f"{x.get('apartment_name')} | "
                f"{x.get('locality')} | "
                f"{x.get('bedroom')}BHK | "
                f"price={x.get('price')} | "
                f"carpet={x.get('carpet_area')} | "
                f"project={x.get('project_id')} | "
                f"live={x.get('is_live')}"
            )

    # ------------------------------------------------------------
    # 2. Same phone + same property/project
    # ------------------------------------------------------------

    phone_groups = defaultdict(list)

    for x in listings:
        phone = norm(x.get("posted_by_contact"))
        if phone:
            phone_groups[phone].append(x)

    print("\n" + "=" * 70)
    print("2. PHONE NUMBERS WITH MANY LISTINGS")
    print("=" * 70)

    repeated_phones = [
        (phone, records)
        for phone, records in phone_groups.items()
        if len(records) >= 3
    ]

    print(f"Phone numbers used by >=3 listings: {len(repeated_phones)}")

    for phone, records in sorted(
        repeated_phones,
        key=lambda p: len(p[1]),
        reverse=True
    )[:30]:
        projects = Counter(x.get("project_id") for x in records)
        localities = Counter(norm(x.get("locality")) for x in records)

        print(
            f"\n{phone} -> {len(records)} listings"
            f" | projects={dict(projects)}"
            f" | localities={dict(localities)}"
        )

        for x in records:
            print(
                f"  {x['listing_id']} | "
                f"{x.get('apartment_name')} | "
                f"{x.get('locality')} | "
                f"{x.get('bedroom')}BHK | "
                f"₹{x.get('price')}"
            )

    # ------------------------------------------------------------
    # 3. Same phone + same project
    # ------------------------------------------------------------

    phone_project = defaultdict(list)

    for x in listings:
        phone = norm(x.get("posted_by_contact"))
        project = norm(x.get("project_id"))

        if phone and project:
            phone_project[(phone, project)].append(x)

    suspicious_phone_project = [
        (key, records)
        for key, records in phone_project.items()
        if len(records) >= 2
    ]

    print("\n" + "=" * 70)
    print("3. SAME PHONE + SAME PROJECT")
    print("=" * 70)
    print(f"Groups: {len(suspicious_phone_project)}")

    for (phone, project), records in sorted(
        suspicious_phone_project,
        key=lambda p: len(p[1]),
        reverse=True
    )[:50]:
        print(
            f"\nphone={phone} project={project} "
            f"records={len(records)}"
        )

        for x in records:
            print(
                f"  {x['listing_id']} | "
                f"{x.get('apartment_name')} | "
                f"{x.get('bedroom')}BHK | "
                f"floor={x.get('floor')} | "
                f"price={x.get('price')} | "
                f"area={x.get('carpet_area')}"
            )

    # ------------------------------------------------------------
    # 4. Same coordinates + same project
    # ------------------------------------------------------------

    coordinate_project = defaultdict(list)

    for x in listings:
        lat = x.get("latitude")
        lon = x.get("longitude")
        project = x.get("project_id")

        if lat is not None and lon is not None and project:
            coordinate_project[(lat, lon, project)].append(x)

    duplicate_coord_groups = [
        (key, records)
        for key, records in coordinate_project.items()
        if len(records) >= 2
    ]

    print("\n" + "=" * 70)
    print("4. SAME COORDINATES + SAME PROJECT")
    print("=" * 70)
    print(f"Groups: {len(duplicate_coord_groups)}")

    for (lat, lon, project), records in sorted(
        duplicate_coord_groups,
        key=lambda p: len(p[1]),
        reverse=True
    )[:50]:
        print(
            f"\nproject={project} "
            f"coords=({lat}, {lon}) "
            f"records={len(records)}"
        )

        for x in records:
            print(
                f"  {x['listing_id']} | "
                f"{x.get('apartment_name')} | "
                f"{x.get('bedroom')}BHK | "
                f"price={x.get('price')} | "
                f"area={x.get('carpet_area')}"
            )

    # ------------------------------------------------------------
    # 5. Same description
    # ------------------------------------------------------------

    descriptions = defaultdict(list)

    for x in listings:
        desc = norm(x.get("description"))
        if desc:
            descriptions[desc].append(x)

    repeated_descriptions = [
        (desc, records)
        for desc, records in descriptions.items()
        if len(records) >= 2
    ]

    print("\n" + "=" * 70)
    print("5. IDENTICAL DESCRIPTIONS")
    print("=" * 70)
    print(f"Groups: {len(repeated_descriptions)}")

    for desc, records in sorted(
        repeated_descriptions,
        key=lambda p: len(p[1]),
        reverse=True
    )[:30]:
        print(f"\nRecords={len(records)}")
        print(f"Description: {desc[:250]}")

        for x in records:
            print(
                f"  {x['listing_id']} | "
                f"{x.get('apartment_name')} | "
                f"{x.get('locality')} | "
                f"price={x.get('price')}"
            )

    # ------------------------------------------------------------
    # 6. Same poster identity across different property facts
    # ------------------------------------------------------------

    poster_groups = defaultdict(list)

    for x in listings:
        poster = norm(x.get("posted_by"))
        if poster:
            poster_groups[poster].append(x)

    print("\n" + "=" * 70)
    print("6. POSTERS WITH MANY LISTINGS")
    print("=" * 70)

    for poster, records in sorted(
        poster_groups.items(),
        key=lambda p: len(p[1]),
        reverse=True
    )[:30]:
        print(f"\n{poster}: {len(records)} listings")

        for x in records[:20]:
            print(
                f"  {x['listing_id']} | "
                f"{x.get('apartment_name')} | "
                f"{x.get('locality')} | "
                f"{x.get('bedroom')}BHK | "
                f"₹{x.get('price')}"
            )


if __name__ == "__main__":
    main()