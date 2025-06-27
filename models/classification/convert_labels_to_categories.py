import json

with open("labels.json", "r", encoding="utf-8") as f:
    labels = json.load(f)

categories = {}
for idx, name in labels.items():
    categories[idx] = {"name": name, "species_id": name}

with open("categories.json", "w", encoding="utf-8") as f:
    json.dump(categories, f, indent=2, ensure_ascii=False)

print("categories.json created successfully!")