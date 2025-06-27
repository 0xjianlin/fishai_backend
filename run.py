import os
import uvicorn
from dotenv import load_dotenv
from app.utils.data_importer import import_data

def main():
    # Load environment variables
    load_dotenv()
    
    # Import data if needed
    if os.getenv("IMPORT_DATA", "false").lower() == "true":
        print("Importing regulation data...")
        import_data()
        print("Data import complete!")

    # Get server configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    # Run the server
    print(f"Starting server at http://{host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug
    )

if __name__ == "__main__":
    main() 