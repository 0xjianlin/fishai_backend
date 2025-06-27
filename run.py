import uvicorn

def main():
    # Run the server
    print("Starting Fishing-AI API server...")
    print("Server will be available at http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main() 