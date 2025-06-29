import json

# File paths
CATEGORIES_PATH = r"D:/Fishing-AI/fishai_backend/models/classification/categories.json"
REGULATIONS_PATH = r"D:/Fishing-AI/fishai_backend/references/regulation/regulations.json"

# Load regulations species
with open(REGULATIONS_PATH, "r", encoding="utf-8") as f:
    regulations = json.load(f)
reg_species = set(entry["species"].strip().lower() for entry in regulations["regulations"] if "species" in entry)

# Load categories species with location California
with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
    categories = json.load(f)
cat_species = set(
    entry["name"].strip().lower()
    for entry in categories["categories"].values()
    if entry.get("location", "") == "California"
)

# Find missing
missing = reg_species - cat_species

print("Missing species in categories.json:")
for species in missing:
    print(species) 