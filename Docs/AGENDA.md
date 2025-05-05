##04/30/2025
create test cases for /store
* Write initial test cases for the /store endpoint (tests/test\_cache\_server.py), covering valid payload and invalid payload scenarios (TDD).  
* Write the main Python file (main.py) for the Cache Server.  
* Define Pydantic models for the StoreRequest payload structure.  
* Initialize the chosen vector database client (ChromaDB or LanceDB), configuring it to persist data to a specific directory *within the container's filesystem* (you will map this to your 1.5TB server storage during deployment).  
* Implement the POST /store endpoint logic based on the StoreRequest model. Focus on receiving the data and successfully adding it to the database collection. Include basic error handling for the database operation.  
* Run the tests for the /store endpoint (pytest tests/test\_cache\_server.py). Debug the implementation until all /store tests pass.  
* Add the Uvicorn runner code to main.py so the FastAPI application can be run by Uvicorn.  
* Create a Dockerfile in the cache\_server directory. This Dockerfile should:  
  * Use a suitable Python base image (e.g., python:3.10-slim).  
  * Set a working directory.  
  * Copy requirements.txt (create this file listing your dependencies: fastapi, uvicorn, chromadb/lancedb, pydantic) and install dependencies.  
  * Copy your application code (main.py, tests/, etc.).  
  * Expose the port your FastAPI app will run on (e.g., 8001).  
  * Define the command to run the application using Uvicorn.  
* Build the Cache Server Docker image on your development machine (e.g., docker build \-t smart-cache-server ./cache\_server).  
* **Manual Testing (Development Machine):** Run the Docker container locally (docker run \-p 8001:8001 \-v /local/test/data:/app/cache\_data smart-cache-server). Use curl or Insomnia/Postman to test the running /store endpoint via http://localhost:8001. Verify data is written to the local test data directory you mapped.