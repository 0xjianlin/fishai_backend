from typing import List, Dict, Optional
from pydantic import BaseModel
import json
from pathlib import Path

class FishingRegulation(BaseModel):
    species_id: str
    water_type: str  # "freshwater" or "ocean"
    min_size: Optional[float] = None  # in cm
    max_size: Optional[float] = None  # in cm
    bag_limit: Optional[int] = None
    season_start: Optional[str] = None  # MM-DD format
    season_end: Optional[str] = None    # MM-DD format
    special_notes: Optional[str] = None
    location: Optional[str] = None      # Specific location if applicable

class RegulationsService:
    def __init__(self):
        self.freshwater_regs: Dict[str, List[FishingRegulation]] = {}
        self.ocean_regs: Dict[str, List[FishingRegulation]] = {}
        self._load_regulations()

    def _load_regulations(self):
        """Load regulations from JSON files"""
        try:
            ref_path = Path(__file__).parent.parent.parent / "references"
            
            # Load freshwater regulations
            fresh_file = ref_path / "freshwater_sport_fishing_regulations.json"
            if fresh_file.exists():
                with open(fresh_file, 'r') as f:
                    data = json.load(f)
                    for reg in data:
                        species_id = reg.get('species_id')
                        if species_id:
                            if species_id not in self.freshwater_regs:
                                self.freshwater_regs[species_id] = []
                            self.freshwater_regs[species_id].append(FishingRegulation(**reg))

            # Load ocean regulations
            ocean_file = ref_path / "ocean_sport_fishing_regulations.json"
            if ocean_file.exists():
                with open(ocean_file, 'r') as f:
                    data = json.load(f)
                    for reg in data:
                        species_id = reg.get('species_id')
                        if species_id:
                            if species_id not in self.ocean_regs:
                                self.ocean_regs[species_id] = []
                            self.ocean_regs[species_id].append(FishingRegulation(**reg))

        except Exception as e:
            print(f"Error loading regulations: {e}")

    def get_regulations(self, species_id: str, water_type: Optional[str] = None) -> List[FishingRegulation]:
        """Get regulations for a species, optionally filtered by water type"""
        regulations = []
        
        if water_type is None or water_type == "freshwater":
            regulations.extend(self.freshwater_regs.get(species_id, []))
        
        if water_type is None or water_type == "ocean":
            regulations.extend(self.ocean_regs.get(species_id, []))
            
        return regulations

    def get_all_regulations(self, water_type: Optional[str] = None) -> Dict[str, List[FishingRegulation]]:
        """Get all regulations, optionally filtered by water type"""
        all_regs = {}
        
        if water_type is None or water_type == "freshwater":
            all_regs.update(self.freshwater_regs)
            
        if water_type is None or water_type == "ocean":
            for species_id, regs in self.ocean_regs.items():
                if species_id in all_regs:
                    all_regs[species_id].extend(regs)
                else:
                    all_regs[species_id] = regs
                    
        return all_regs

# Create a singleton instance
regulations_service = RegulationsService() 