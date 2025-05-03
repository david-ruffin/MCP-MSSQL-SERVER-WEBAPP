from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging

from .answer import answer_question
from .config import HOST, PORT, DEBUG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Initialize FastAPI app
app = FastAPI(
    title="SQL Chat API",
    description="A natural language interface to SQL databases",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define request/response models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    sql_query: Optional[str] = None
    result: Optional[dict] = None
    answer: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Welcome to the SQL Chat API. Send questions to /query."}

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        logger.info(f"Received question: {request.question}")
        result = answer_question(request.question)
        return result
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def start_server():
    """Start the FastAPI application using Uvicorn"""
    uvicorn.run("app.api:app", host=HOST, port=PORT, reload=DEBUG)

if __name__ == "__main__":
    start_server()