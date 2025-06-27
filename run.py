import uvicorn
import os

def main():
    # Get port from environment variable (Railway provides this)
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server
    print("Starting Fishing-AI API server...")
    print(f"Server will be available at http://0.0.0.0:{port}")
    print(f"API documentation: http://0.0.0.0:{port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload in production
    )

if __name__ == "__main__":
    main() 