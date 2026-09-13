import json
from collections import defaultdict

with open("investigation/data/listings.json", "r", encoding="utf-8") as f:
    data = json.load(f)

listings = data["listings"]

groups = defaultdict(list)

for x in listings:
    groups[(x["latitude"], x["longitude"])].append(x)


duplicate_groups = [
    (coords, records)
    for coords, records in groups.items()
    if len(records) > 1
]

print("=" * 70)
print("PROPERTY IDENTITY VERIFICATION")
print("=" * 70)

print("Coordinate duplicate groups:", len(duplicate_groups))

# Show the first 20 groups with their important identity fields.
for coords, records in sorted(
    duplicate_groups,
    key=lambda item: len(item[1]),
    reverse=True
)[:20]:

    print("\nCoordinates:", coords)
    print("Records:", len(records))

    for x in records:
        print(
            f"  {x['listing_id']}"
            f" | project={x.get('project_id')}"
            f" | name={x.get('apartment_name')}"
            f" | locality={x.get('locality')}"
            f" | bed={x.get('bedroom')}"
            f" | bath={x.get('bathroom')}"
            f" | carpet={x.get('carpet_area')}"
            f" | super={x.get('super_built_up_area')}"
            f" | price={x.get('price')}"
        )