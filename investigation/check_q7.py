import json

with open("investigation/data/projects.json", encoding="utf-8") as f:
    projects = json.load(f)["results"]

with open("investigation/data/listings.json", encoding="utf-8") as f:
    listings = json.load(f)["listings"]

p = next(x for x in projects if x["project_id"] == "P60090")

print("=== PROJECT P60090 ===")
for k in [
    "project_id",
    "apartment_name",
    "locality",
    "total_units",
    "total_listings",
    "price_min",
    "price_max",
]:
    print(f"{k}: {p.get(k)}")

print("\n=== LISTINGS WITH project_id=P60090 ===")
matches = [x for x in listings if x.get("project_id") == "P60090"]

for x in matches:
    print(
        x["listing_id"],
        "| price =", x["price"],
        "| bedroom =", x["bedroom"],
        "| carpet =", x["carpet_area"],
        "| live =", x["is_live"],
        "| locality =", x["locality"],
    )

print("\nListing price min/max:")
prices = [x["price"] for x in matches]
print(min(prices), max(prices))

print("\nProject price_max:", p["price_max"])
print("Listing max / project price_max:", max(prices) / p["price_max"])

print("\nCandidate conversions:")
for multiplier, name in [
    (100_000, "lakh"),
    (1_000_000, "million"),
    (10_000_000, "crore"),
]:
    converted = p["price_max"] * multiplier
    print(f"{name:8s}: {converted:,.0f} INR")
