import json
import yaml

# File paths
CATEGORIES_PATH = r"D:/Fishing-AI/fishai_backend/models/classification/categories.json"
PENDING_PATH = r"D:/Fishing-AI/fishai_backend/models/classification/pending.yaml"
REGULATIONS_PATH = r"D:/Fishing-AI/fishai_backend/references/regulation/regulations.json"

def load_regulation_species_and_ids(regulations_path):
    with open(regulations_path, "r", encoding="utf-8") as f:
        regulations = json.load(f)
    # Map species name (lowercase) to latin_name (species_id)
    species_to_id = {}
    for entry in regulations["regulations"]:
        if "species" in entry and "latin_name" in entry:
            species_to_id[entry["species"].strip().lower()] = entry["latin_name"]
    return species_to_id

def load_pending(pending_path):
    with open(pending_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def add_to_categories(categories_path, pending, species_to_id):
    with open(categories_path, "r", encoding="utf-8") as f:
        categories = json.load(f)

    # Find the next available integer key
    existing_keys = [int(k) for k in categories["categories"].keys()]
    next_key = max(existing_keys) + 1 if existing_keys else 1

    added_count = 0
    for name, image_url in pending.items():
        key = name.strip().lower()
        if key in species_to_id:
            categories["categories"][str(next_key)] = {
                "name": name,
                "image_url": image_url,
                "species_id": species_to_id[key],
                "location": "California"
            }
            next_key += 1
            added_count += 1

    with open(categories_path, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)

    print(f"Added {added_count} items from pending.yaml to categories.json.")

def main():
    species_to_id = load_regulation_species_and_ids(REGULATIONS_PATH)
    pending = load_pending(PENDING_PATH)
    add_to_categories(CATEGORIES_PATH, pending, species_to_id)

if __name__ == "__main__":
    main() 