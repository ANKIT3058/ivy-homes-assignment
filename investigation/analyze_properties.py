import json
from collections import defaultdict

with open("investigation/data/listings.json", "r", encoding="utf-8") as f:
    data = json.load(f)

listings = data["listings"]

def groups_by(key_fn):
    groups = defaultdict(list)

    for x in listings:
        key = key_fn(x)
        groups[key].append(x["listing_id"])

    return {k: v for k, v in groups.items() if len(v) > 1}


# ------------------------------------------------------------
# 1. Exact latitude + longitude
# ------------------------------------------------------------

exact_coords = groups_by(
    lambda x: (x["latitude"], x["longitude"])
)

print("=" * 70)
print("EXACT COORDINATE DUPLICATES")
print("=" * 70)

print("Groups:", len(exact_coords))
print("Records involved:", sum(len(v) for v in exact_coords.values()))

for coords, ids in sorted(
    exact_coords.items(),
    key=lambda kv: len(kv[1]),
    reverse=True
)[:30]:
    print(coords, "|", len(ids), "|", ", ".join(ids))


# ------------------------------------------------------------
# 2. project_id + locality
# ------------------------------------------------------------

project_groups = groups_by(
    lambda x: (
        x.get("project_id"),
        x.get("locality"),
    )
)

print("\n" + "=" * 70)
print("PROJECT + LOCALITY DUPLICATES")
print("=" * 70)

print("Groups:", len(project_groups))
print("Records involved:", sum(len(v) for v in project_groups.values()))

for key, ids in sorted(
    project_groups.items(),
    key=lambda kv: len(kv[1]),
    reverse=True
)[:30]:
    print(key, "|", len(ids), "|", ", ".join(ids))


# ------------------------------------------------------------
# 3. apartment_name + locality
# ------------------------------------------------------------

name_groups = groups_by(
    lambda x: (
        str(x.get("apartment_name", "")).strip().lower(),
        str(x.get("locality", "")).strip().lower(),
    )
)

print("\n" + "=" * 70)
print("APARTMENT NAME + LOCALITY DUPLICATES")
print("=" * 70)

print("Groups:", len(name_groups))
print("Records involved:", sum(len(v) for v in name_groups.values()))

for key, ids in sorted(
    name_groups.items(),
    key=lambda kv: len(kv[1]),
    reverse=True
)[:30]:
    print(key, "|", len(ids), "|", ", ".join(ids))