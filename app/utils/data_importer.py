import json
from pathlib import Path
from typing import Dict, List
import logging
from ..services.species_service import FishSpecies
from ..services.regulations_service import FishingRegulation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataImporter:
    def __init__(self):
        self.ref_path = Path(__file__).parent.parent.parent / "references"
        self.species_data: Dict[str, FishSpecies] = {}
        self.freshwater_regs: Dict[str, List[FishingRegulation]] = {}
        self.ocean_regs: Dict[str, List[FishingRegulation]] = {}

    def import_regulations(self):
        """Import and process regulation data from JSON files"""
        try:
            # Import freshwater regulations
            fresh_file = self.ref_path / "freshwater_sport_fishing_regulations.json"
            if fresh_file.exists():
                logger.info("Importing freshwater regulations...")
                with open(fresh_file, 'r') as f:
                    data = json.load(f)
                    self._process_regulations(data, "freshwater")
                logger.info(f"Imported {len(self.freshwater_regs)} freshwater species regulations")
            else:
                logger.warning("Freshwater regulations file not found")

            # Import ocean regulations
            ocean_file = self.ref_path / "ocean_sport_fishing_regulations.json"
            if ocean_file.exists():
                logger.info("Importing ocean regulations...")
                with open(ocean_file, 'r') as f:
                    data = json.load(f)
                    self._process_regulations(data, "ocean")
                logger.info(f"Imported {len(self.ocean_regs)} ocean species regulations")
            else:
                logger.warning("Ocean regulations file not found")

            # Save processed data
            self._save_processed_data()

        except Exception as e:
            logger.error(f"Error importing regulations: {e}")
            raise

    def _process_regulations(self, data: List[Dict], water_type: str):
        """Process regulation data and extract species information"""
        for reg in data:
            try:
                # Extract species information
                species_id = reg.get('species_id')
                if not species_id:
                    continue

                # Create or update species data
                if species_id not in self.species_data:
                    self.species_data[species_id] = FishSpecies(
                        id=species_id,
                        common_name=reg.get('common_name', 'Unknown'),
                        scientific_name=reg.get('scientific_name', ''),
                        description=reg.get('description'),
                        habitat=reg.get('habitat'),
                        average_size=reg.get('average_size'),
                        record_size=reg.get('record_size')
                    )

                # Create regulation
                regulation = FishingRegulation(
                    species_id=species_id,
                    water_type=water_type,
                    min_size=reg.get('min_size'),
                    max_size=reg.get('max_size'),
                    bag_limit=reg.get('bag_limit'),
                    season_start=reg.get('season_start'),
                    season_end=reg.get('season_end'),
                    special_notes=reg.get('special_notes'),
                    location=reg.get('location')
                )

                # Add to appropriate regulations dict
                if water_type == "freshwater":
                    if species_id not in self.freshwater_regs:
                        self.freshwater_regs[species_id] = []
                    self.freshwater_regs[species_id].append(regulation)
                else:
                    if species_id not in self.ocean_regs:
                        self.ocean_regs[species_id] = []
                    self.ocean_regs[species_id].append(regulation)

            except Exception as e:
                logger.error(f"Error processing regulation for {reg.get('species_id', 'unknown')}: {e}")

    def _save_processed_data(self):
        """Save processed data to JSON files"""
        try:
            # Save species data
            species_file = self.ref_path / "processed_species_data.json"
            with open(species_file, 'w') as f:
                json.dump([s.dict() for s in self.species_data.values()], f, indent=2)
            logger.info(f"Saved {len(self.species_data)} species records")

            # Save freshwater regulations
            fresh_file = self.ref_path / "processed_freshwater_regs.json"
            with open(fresh_file, 'w') as f:
                json.dump({
                    species_id: [r.dict() for r in regs]
                    for species_id, regs in self.freshwater_regs.items()
                }, f, indent=2)
            logger.info(f"Saved {len(self.freshwater_regs)} freshwater regulation records")

            # Save ocean regulations
            ocean_file = self.ref_path / "processed_ocean_regs.json"
            with open(ocean_file, 'w') as f:
                json.dump({
                    species_id: [r.dict() for r in regs]
                    for species_id, regs in self.ocean_regs.items()
                }, f, indent=2)
            logger.info(f"Saved {len(self.ocean_regs)} ocean regulation records")

        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
            raise

def import_data():
    """Main function to run the import process"""
    importer = DataImporter()
    importer.import_regulations()

if __name__ == "__main__":
    import_data() 