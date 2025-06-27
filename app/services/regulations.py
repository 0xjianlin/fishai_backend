from typing import Dict, Optional
from ..models.species import Regulation
import json
import os
from pathlib import Path

# TODO: Replace with actual regulations data
REGULATIONS_DATA = {
    "vermilion_rockfish": {
        "min_size": 10.0,
        "bag_limit": 4,
        "season_start": "01-01",
        "season_end": "12-31",
        "notes": "Part of the Rockfish complex",
        "gear_restrictions": ["Hook and line only"],
        "special_restrictions": ["Must be landed with head and tail intact"]
    },
    "bocaccio": {
        "min_size": 10.0,
        "bag_limit": 1,
        "season_start": "01-01",
        "season_end": "12-31",
        "notes": "Part of the Rockfish complex",
        "gear_restrictions": ["Hook and line only"],
        "special_restrictions": ["Must be landed with head and tail intact"]
    }
}

def get_regulations(species_id: str) -> Regulation:
    """
    Get fishing regulations for a specific species
    """
    if species_id not in REGULATIONS_DATA:
        # Return default regulation if species not found
        return Regulation()
    
    return Regulation(**REGULATIONS_DATA[species_id])

def load_regulations_from_file(file_path: Optional[str] = None) -> Dict:
    """
    Load regulations from a JSON file
    TODO: Implement actual JSON file loading
    """
    if file_path is None:
        file_path = Path(__file__).parent.parent / "data" / "regulations.json"
    
    if not os.path.exists(file_path):
        return REGULATIONS_DATA
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading regulations file: {e}")
        return REGULATIONS_DATA 