import json
from collections import defaultdict

with open("investigation/data/listings.json", "r", encoding="utf-8") as f:
    data = json.load(f)

listings = data["listings"]


def analyze(name, key_fn):
    groups = defaultdict(list)

    for x in listings:
        key = key_fn(x)
        groups[key].append(x["listing_id"])

    groups = {
        k: v for k, v in groups.items()
        if len(v) > 1
    }

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)
    print("Duplicate groups:", len(groups))
    print("Records involved:", sum(len(v) for v in groups.values()))

    for key, ids in sorted(
        groups.items(),
        key=lambda kv: len(kv[1]),
        reverse=True
    )[:20]:
        print(key, "|", len(ids), "|", ", ".join(ids))


# 1. Apartment + locality + bedroom + bathroom + areas
analyze(
    "NAME + LOCALITY + BED + BATH + AREAS",
    lambda x: (
        str(x.get("apartment_name", "")).strip().lower(),
        str(x.get("locality", "")).strip().lower(),
        x.get("bedroom"),
        x.get("bathroom"),
        x.get("carpet_area"),
        x.get("super_built_up_area"),
    )
)


# 2. Apartment + locality + bedroom + areas
analyze(
    "NAME + LOCALITY + BED + AREAS",
    lambda x: (
        str(x.get("apartment_name", "")).strip().lower(),
        str(x.get("locality", "")).strip().lower(),
        x.get("bedroom"),
        x.get("carpet_area"),
        x.get("super_built_up_area"),
    )
)


# 3. Project + bedroom + bathroom + areas
analyze(
    "PROJECT + BED + BATH + AREAS",
    lambda x: (
        x.get("project_id"),
        x.get("bedroom"),
        x.get("bathroom"),
        x.get("carpet_area"),
        x.get("super_built_up_area"),
    )
)


# 4. Apartment + locality + bedroom + bathroom + price + areas
analyze(
    "NAME + LOCALITY + BED + BATH + PRICE + AREAS",
    lambda x: (
        str(x.get("apartment_name", "")).strip().lower(),
        str(x.get("locality", "")).strip().lower(),
        x.get("bedroom"),
        x.get("bathroom"),
        x.get("price"),
        x.get("carpet_area"),
        x.get("super_built_up_area"),
    )
)