from typing import List, Dict, Optional
from pydantic import BaseModel
import json
from pathlib import Path

class FishSpecies(BaseModel):
    id: str
    common_name: str
    scientific_name: str
    image_url: Optional[str] = None
    description: Optional[str] = None
    habitat: Optional[str] = None
    average_size: Optional[float] = None  # in cm
    record_size: Optional[float] = None   # in cm
    regulations: Optional[Dict] = None

class SpeciesService:
    def __init__(self):
        self.species_data: Dict[str, FishSpecies] = {}
        self._load_species_data()

    def _load_species_data(self):
        """Load species data from JSON files"""
        try:
            # Load from references directory
            ref_path = Path(__file__).parent.parent.parent / "references"
            species_file = ref_path / "species_data.json"
            
            if species_file.exists():
                with open(species_file, 'r') as f:
                    data = json.load(f)
                    for species in data:
                        self.species_data[species['id']] = FishSpecies(**species)
        except Exception as e:
            print(f"Error loading species data: {e}")
            # Initialize with some basic data
            self.species_data = {
                "unknown": FishSpecies(
                    id="unknown",
                    common_name="Unknown Species",
                    scientific_name="",
                    description="Species not identified with high confidence."
                )
            }

    def get_species(self, species_id: str) -> Optional[FishSpecies]:
        """Get species information by ID"""
        return self.species_data.get(species_id)

    def get_all_species(self) -> List[FishSpecies]:
        """Get all species information"""
        return list(self.species_data.values())

    def search_species(self, query: str) -> List[FishSpecies]:
        """Search species by name (common or scientific)"""
        query = query.lower()
        return [
            species for species in self.species_data.values()
            if query in species.common_name.lower() or 
               query in species.scientific_name.lower()
        ]

    def add_species(self, species: FishSpecies):
        """Add a species to the service"""
        self.species_data[species.id] = species

    def get_species_by_common_name(self, common_name: str) -> Optional[FishSpecies]:
        """Get species by common name"""
        for species in self.species_data.values():
            if species.common_name.lower() == common_name.lower():
                return species
        return None

    def get_species_by_scientific_name(self, scientific_name: str) -> Optional[FishSpecies]:
        """Get species by scientific name"""
        for species in self.species_data.values():
            if species.scientific_name.lower() == scientific_name.lower():
                return species
        return None

# Create a singleton instance
species_service = SpeciesService() 