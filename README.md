# Fishing-AI Backend

Backend service for fish species identification and regulation lookup.

## Features

- Fish species identification using Fishial.ai API
- Fishing regulations lookup (freshwater and ocean)
- Species information database
- RESTful API endpoints
- Batch image processing

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:
```env
# Server Configuration
API_HOST=0.0.0.0
API_PORT=8001
DEBUG=True

# API Keys
FISHIAL_API_KEY=your_fishial_api_key_here
CLOUDINARY_URL=your_cloudinary_url_here

# Data Import
IMPORT_DATA=True  # Set to True on first run to import regulation data
```

4. Place regulation JSON files in the `references` directory:
- `freshwater_sport_fishing_regulations.json`
- `ocean_sport_fishing_regulations.json`

## Running the Server

1. Start the server:
```bash
python run.py
```

The server will start at `http://localhost:8001`

2. Access the API documentation:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## API Endpoints

### Species
- `GET /api/species` - Get all species
- `GET /api/species/{species_id}` - Get specific species
- `GET /api/species/search/{query}` - Search species
- `GET /api/species/{species_id}/regulations` - Get regulations for a species

### Regulations
- `GET /api/regulations` - Get all regulations
- `GET /api/regulations?water_type=freshwater` - Get freshwater regulations
- `GET /api/regulations?water_type=ocean` - Get ocean regulations

### Identification
- `POST /api/identify` - Identify fish in a single image
- `POST /api/identify/batch` - Identify fish in multiple images

## Development

### Project Structure
```
backend/
├── app/
│   ├── api/            # API endpoints
│   ├── services/       # Business logic
│   ├── models/         # Data models
│   └── utils/          # Utilities
├── references/         # Data files
├── tests/             # Test files
├── .env               # Environment variables
├── requirements.txt   # Dependencies
└── run.py            # Server entry point
```

### Adding New Features

1. Create new service in `app/services/`
2. Add API endpoints in `app/api/`
3. Update models if needed in `app/models/`
4. Add tests in `tests/`

### Testing

Run tests with:
```bash
pytest
```

## License

MIT License 