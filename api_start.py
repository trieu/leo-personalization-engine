from personalization_router import api_personalization

# Run the FastAPI api_personalization
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api_personalization, host="0.0.0.0", port=8000)