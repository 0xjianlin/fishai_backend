import json

# File paths
CATEGORIES_PATH = r"D:/Fishing-AI/fishai_backend/models/classification/categories.json"
REGULATIONS_PATH = r"D:/Fishing-AI/fishai_backend/references/regulation/regulations.json"

def load_species_from_regulations(regulations_path):
    with open(regulations_path, "r", encoding="utf-8") as f:
        regulations = json.load(f)
    species_set = set()
    for entry in regulations["regulations"]:
        if isinstance(entry, dict):
            if "species" in entry:
                species_set.add(entry["species"].strip().lower())
            elif "common_name" in entry:
                species_set.add(entry["common_name"].strip().lower())
    return species_set

def update_categories(categories_path, species_set):
    with open(categories_path, "r", encoding="utf-8") as f:
        categories = json.load(f)

    for entry in categories["categories"].values():
        species_name = entry.get("name")
        if not species_name:
            entry["location"] = ""
            continue
        if species_name.strip().lower() in species_set:
            entry["location"] = "California"
        else:
            entry["location"] = ""

    with open(categories_path, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)

def main():
    species_set = load_species_from_regulations(REGULATIONS_PATH)
    update_categories(CATEGORIES_PATH, species_set)
    print("categories.json updated with location field.")

if __name__ == "__main__":
    main() 