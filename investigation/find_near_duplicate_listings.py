import json
from collections import defaultdict

with open("investigation/data/listings.json", encoding="utf-8") as f:
    data = json.load(f)

listings = data["listings"]

def norm(x):
    return str(x or "").strip().lower()

# Group by property characteristics while deliberately IGNORING
# contact, description, listing_id, posted_at and website.
#
# If multiple records describe essentially the same physical unit,
# they become candidates for duplicate/fake investigation.
groups = defaultdict(list)

for x in listings:
    key = (
        norm(x.get("apartment_name")),
        norm(x.get("locality")),
        x.get("bedroom"),
        x.get("bathroom"),
        x.get("carpet_area"),
        x.get("super_built_up_area"),
    )
    groups[key].append(x)

print("TOTAL:", len(listings))
print()

multi = [(k, xs) for k, xs in groups.items() if len(xs) >= 2]

print("=== PROPERTY ATTRIBUTE COLLISIONS ===")
print("GROUPS:", len(multi))
print("RECORDS:", sum(len(xs) for _, xs in multi))
print()

for key, xs in sorted(multi, key=lambda z: (-len(z[1]), str(z[0]))):
    print("KEY:", key, "COUNT:", len(xs))
    for x in xs:
        print(
            " ",
            x["listing_id"],
            "| price", x.get("price"),
            "| floor", x.get("floor"),
            "| project", x.get("project_id"),
            "| lat/lon", x.get("latitude"), x.get("longitude"),
            "| phone", x.get("posted_by_contact"),
            "| name", x.get("posted_by_name"),
            "| live", x.get("is_live"),
            "| verified", x.get("is_verified"),
            "| posted", x.get("posted_at"),
        )
    print()


# Now use a stronger physical-location key:
# same property name + BHK + area + coordinates rounded to 3 decimals.
# 0.001 degrees is roughly 100m, so this catches records in the
# same building/location while tolerating tiny coordinate differences.
groups = defaultdict(list)

for x in listings:
    lat = x.get("latitude")
    lon = x.get("longitude")

    if lat is None or lon is None:
        continue

    key = (
        norm(x.get("apartment_name")),
        x.get("bedroom"),
        x.get("carpet_area"),
        round(float(lat), 3),
        round(float(lon), 3),
    )
    groups[key].append(x)

multi = [(k, xs) for k, xs in groups.items() if len(xs) >= 2]

print("=== SAME NAME + BHK + AREA + NEARBY COORDINATES ===")
print("GROUPS:", len(multi))
print()

for key, xs in sorted(multi, key=lambda z: (-len(z[1]), str(z[0]))):
    print("KEY:", key, "COUNT:", len(xs))
    for x in xs:
        print(
            " ",
            x["listing_id"],
            "|", x.get("apartment_name"),
            "| price", x.get("price"),
            "| carpet", x.get("carpet_area"),
            "| super", x.get("super_built_up_area"),
            "| floor", x.get("floor"),
            "| project", x.get("project_id"),
            "| locality", x.get("locality"),
            "| phone", x.get("posted_by_contact"),
            "| live", x.get("is_live"),
            "| verified", x.get("is_verified"),
        )
    print()
