from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime

class Regulation(BaseModel):
    min_size: Optional[float] = None  # in inches
    max_size: Optional[float] = None  # in inches
    bag_limit: Optional[int] = None
    season_start: Optional[str] = None  # MM-DD format
    season_end: Optional[str] = None    # MM-DD format
    notes: Optional[str] = None
    gear_restrictions: Optional[List[str]] = None
    special_restrictions: Optional[List[str]] = None

class Species(BaseModel):
    id: str
    name: str
    scientific_name: str
    regulations: Regulation
    image_url: Optional[str] = None
    description: Optional[str] = None
    habitat: Optional[str] = None
    average_size: Optional[float] = None  # in inches
    record_size: Optional[float] = None   # in inches

class SpeciesResponse(BaseModel):
    id: str
    name: str
    scientific_name: str
    regulations: Regulation
    image_url: Optional[str] = None
    description: Optional[str] = None
    habitat: Optional[str] = None
    average_size: Optional[float] = None
    record_size: Optional[float] = None

    @classmethod
    def from_species(cls, species: Species) -> "SpeciesResponse":
        return cls(**species.dict())

class PredictionResult(BaseModel):
    species_id: str
    confidence: float
    species_info: SpeciesResponse 