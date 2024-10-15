from personalization_router import api_personalization

from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv(override=True)

# Fetch the host and port from environment variables
host = os.getenv('FASTAPI_HOST', '0.0.0.0')  # default is '0.0.0.0'
port = int(os.getenv('FASTAPI_PORT', 8000))  # default is 8000

# Run the FastAPI api_personalization
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api_personalization, host=host, port=port)