import json
from collections import defaultdict, Counter

with open("investigation/data/listings.json", encoding="utf-8") as f:
    data = json.load(f)

listings = data["listings"]

def norm(x):
    return str(x or "").strip().lower()

# 1. Same phone + same name + same BHK + same area
groups = defaultdict(list)
for x in listings:
    key = (
        norm(x.get("posted_by_contact")),
        norm(x.get("posted_by_name")),
        x.get("bedroom"),
        x.get("carpet_area"),
    )
    groups[key].append(x)

print("=== SAME PHONE + NAME + BHK + CARPET ===")
found = 0
for key, xs in groups.items():
    if key[0] and len(xs) >= 2:
        print()
        print("KEY:", key, "COUNT:", len(xs))
        for x in xs:
            print(
                x["listing_id"],
                "|", x.get("apartment_name"),
                "| price", x.get("price"),
                "| super", x.get("super_built_up_area"),
                "| floor", x.get("floor"),
                "| project", x.get("project_id"),
                "| locality", x.get("locality"),
                "| live", x.get("is_live"),
                "| verified", x.get("is_verified"),
            )
        found += 1

print("GROUPS:", found)


# 2. Same phone + same name + same BHK + same area + same price
groups = defaultdict(list)
for x in listings:
    key = (
        norm(x.get("posted_by_contact")),
        norm(x.get("posted_by_name")),
        x.get("bedroom"),
        x.get("carpet_area"),
        x.get("price"),
    )
    groups[key].append(x)

print("\n=== SAME PHONE + NAME + BHK + AREA + PRICE ===")
found = 0
for key, xs in groups.items():
    if key[0] and len(xs) >= 2:
        print()
        print("KEY:", key, "COUNT:", len(xs))
        for x in xs:
            print(
                x["listing_id"],
                "|", x.get("apartment_name"),
                "| super", x.get("super_built_up_area"),
                "| floor", x.get("floor"),
                "| project", x.get("project_id"),
                "| locality", x.get("locality"),
                "| live", x.get("is_live"),
                "| verified", x.get("is_verified"),
            )
        found += 1

print("GROUPS:", found)


# 3. Same phone + same property name + same BHK + same price + same area
#    but DIFFERENT project/listing IDs
#    This is a particularly strong duplicate/fraud signal.
groups = defaultdict(list)
for x in listings:
    key = (
        norm(x.get("posted_by_contact")),
        norm(x.get("apartment_name")),
        x.get("bedroom"),
        x.get("carpet_area"),
        x.get("price"),
    )
    groups[key].append(x)

print("\n=== SAME PHONE + PROPERTY + BHK + AREA + PRICE ===")
found = 0
for key, xs in groups.items():
    if key[0] and len(xs) >= 2:
        print()
        print("KEY:", key, "COUNT:", len(xs))
        for x in xs:
            print(
                x["listing_id"],
                "|", x.get("apartment_name"),
                "| floor", x.get("floor"),
                "| super", x.get("super_built_up_area"),
                "| project", x.get("project_id"),
                "| locality", x.get("locality"),
                "| posted", x.get("posted_at"),
                "| live", x.get("is_live"),
                "| verified", x.get("is_verified"),
            )
        found += 1

print("GROUPS:", found)


# 4. Poster statistics
print("\n=== POSTER TYPE ===")
print(Counter(norm(x.get("posted_by")) for x in listings))

# 5. Unverified active listings
print("\n=== LIVE + UNVERIFIED COUNT ===")
xs = [
    x for x in listings
    if x.get("is_live") is True and x.get("is_verified") is False
]
print(len(xs))

# Show unusual repeated contacts among live+unverified
phones = defaultdict(list)
for x in xs:
    phone = norm(x.get("posted_by_contact"))
    if phone:
        phones[phone].append(x)

print("\n=== LIVE+UNVERIFIED REPEATED PHONES ===")
for phone, ys in sorted(phones.items(), key=lambda p: -len(p[1])):
    if len(ys) >= 3:
        print("\nPHONE:", phone, "COUNT:", len(ys))
        for x in ys:
            print(
                x["listing_id"],
                "|", x.get("apartment_name"),
                "|", x.get("bedroom"), "BHK",
                "|", x.get("carpet_area"),
                "|", x.get("price"),
                "|", x.get("locality"),
            )
