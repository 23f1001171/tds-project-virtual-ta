# main.py (or your FastAPI entry file)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from qa_pipeline import get_relevant_answer

app = FastAPI()

# Add this entire origins section to allow requests
# from the evaluation website and local development.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define your data models using Pydantic
class Link(BaseModel):
    text: str
    url: str

class RequestBody(BaseModel):
    question: str
    image: str | None = None # Optional image field

class ResponseBody(BaseModel):
    answer: str
    links: List[Link]


@app.post("/")
def handle_request(body: RequestBody) -> ResponseBody:
    # Use your QA pipeline to get an answer
    answer_text, links = get_relevant_answer(body.question, body.image)

    return ResponseBody(
        answer=answer_text,
        links=[Link(text=link["text"], url=link["url"]) for link in links]
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/query")
async def query(request: Request):
    data = await request.json()
    question = data.get("question", "")
    return {"answer": f"You asked: {question}"}
