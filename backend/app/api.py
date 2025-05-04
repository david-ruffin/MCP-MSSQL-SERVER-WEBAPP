from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from .answer import answer_question
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Natural Language SQL Chat")

# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sql: Optional[str] = None


@app.get("/")
async def root():
    return {"message": "Natural Language SQL Chat API is running"}


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        logger.info(f"Received question: {request.question}")
        result = answer_question(request.question)
        
        # Check if result is a dictionary with both answer and SQL
        if isinstance(result, dict) and "answer" in result:
            return QueryResponse(
                answer=result["answer"],
                sql=result.get("sql")
            )
        
        # Otherwise, assume it's just a string answer
        return QueryResponse(answer=result)

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status code: {response.status_code}")
    return response