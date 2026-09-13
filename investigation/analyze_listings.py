import json
from collections import Counter
from pathlib import Path


DATA_FILE = Path(__file__).parent / "data" / "listings.json"

REFERENCE_DATE = "2026-09-10T00:00:00+05:30"
ASSIGNED_LOCALITY = "sohna road"


def load_listings():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data["listings"]


def normalize(value):
    if isinstance(value, str):
        return value.strip().lower()
    return value


def main():
    listings = load_listings()

    print("=" * 60)
    print("LISTING DATASET ANALYSIS")
    print("=" * 60)

    # ---------------------------------------------------------
    # Q1 — Total listing records
    # ---------------------------------------------------------

    print("\nQ1 — Total listing records")
    print(f"Total records: {len(listings)}")

    # ---------------------------------------------------------
    # Basic listing-ID analysis
    # ---------------------------------------------------------

    listing_ids = [listing.get("listing_id") for listing in listings]
    id_counts = Counter(listing_ids)

    duplicate_ids = {
        listing_id: count
        for listing_id, count in id_counts.items()
        if count > 1
    }

    print("\nListing ID integrity")
    print(f"Unique listing IDs: {len(id_counts)}")
    print(f"Duplicate listing IDs: {len(duplicate_ids)}")

    # ---------------------------------------------------------
    # Q3 — Active listings
    # ---------------------------------------------------------

    active = [
        listing
        for listing in listings
        if listing.get("is_live") is True
    ]

    print("\nQ3 — Active listings")
    print(f"Active listings: {len(active)}")

    # ---------------------------------------------------------
    # Locality analysis
    # ---------------------------------------------------------

    locality_counts = Counter(
        normalize(listing.get("locality"))
        for listing in listings
    )

    print("\nLocality check")
    print(
        f"'{ASSIGNED_LOCALITY}' records: "
        f"{locality_counts.get(ASSIGNED_LOCALITY, 0)}"
    )

    # ---------------------------------------------------------
    # Q5 — Total monthly rent in assigned locality
    # ---------------------------------------------------------

    # We will inspect property_type values first because the
    # dataset may represent rentals differently.
    locality_listings = [
        listing
        for listing in listings
        if normalize(listing.get("locality")) == ASSIGNED_LOCALITY
    ]

    print("\nSohna Road listings")

    property_types = Counter(
        normalize(listing.get("property_type"))
        for listing in locality_listings
    )

    print("Property types:")
    for property_type, count in property_types.items():
        print(f"  {property_type}: {count}")

    print(f"Total records: {len(locality_listings)}")

    # ---------------------------------------------------------
    # Bedrooms
    # ---------------------------------------------------------

    print("\nBedroom distribution")

    bedroom_counts = Counter(
        listing.get("bedroom")
        for listing in listings
    )

    for bedroom, count in sorted(
        bedroom_counts.items(),
        key=lambda x: str(x[0])
    ):
        print(f"  {bedroom}: {count}")

    # ---------------------------------------------------------
    # Price / area sanity checks
    # ---------------------------------------------------------

    print("\nPrice / area sanity checks")

    missing_price = [
        listing
        for listing in listings
        if listing.get("price") is None
    ]

    missing_area = [
        listing
        for listing in listings
        if listing.get("carpet_area") is None
    ]

    print(f"Missing price: {len(missing_price)}")
    print(f"Missing carpet area: {len(missing_area)}")

    # ---------------------------------------------------------
    # Posted-at range
    # ---------------------------------------------------------

    posted_dates = [
        listing.get("posted_at")
        for listing in listings
        if listing.get("posted_at")
    ]

    print("\nPosted-at range")

    if posted_dates:
        print(f"Earliest: {min(posted_dates)}")
        print(f"Latest:   {max(posted_dates)}")

    # ---------------------------------------------------------
    # Show suspiciously small carpet areas
    # ---------------------------------------------------------

    suspicious_area = [
        listing
        for listing in listings
        if isinstance(listing.get("carpet_area"), (int, float))
        and listing["carpet_area"] < 200
    ]

    print("\nListings with carpet area < 200 sqft")
    print(f"Count: {len(suspicious_area)}")

    for listing in suspicious_area[:20]:
        print(
            f"  {listing.get('listing_id')} | "
            f"{listing.get('bedroom')} BHK | "
            f"{listing.get('carpet_area')} sqft | "
            f"{listing.get('locality')}"
        )

    # ---------------------------------------------------------
    # Dataset field inventory
    # ---------------------------------------------------------

    fields = set()

    for listing in listings:
        fields.update(listing.keys())

    print("\nFields")
    for field in sorted(fields):
        print(f"  {field}")


if __name__ == "__main__":
    main()