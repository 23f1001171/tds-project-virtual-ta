from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from qa_pipeline import get_relevant_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In prod, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Link(BaseModel):
    text: str
    url: str

class RequestBody(BaseModel):
    question: str
    image: Optional[str] = None

class ResponseBody(BaseModel):
    answer: str
    links: List[Link]


@app.post("/", response_model=ResponseBody)
def handle_request(body: RequestBody) -> ResponseBody:
    answer_text, links = get_relevant_answer(body.question, body.image)
    return ResponseBody(
        answer=answer_text,
        links=[Link(text=link["text"], url=link["url"]) for link in links]
    )

@app.post("/query", response_model=ResponseBody)
async def query(request: Request) -> ResponseBody:
    data = await request.json()
    question = data.get("question", "")
    image = data.get("image", None)

    answer_text, links = get_relevant_answer(question, image)
    return ResponseBody(
        answer=answer_text,
        links=[Link(text=link["text"], url=link["url"]) for link in links]
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}
