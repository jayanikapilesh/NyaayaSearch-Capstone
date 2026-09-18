from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from search_core import SearchEngine
from rag_core import generate_explanation

app = FastAPI(title="NyaayaSearch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = None


@app.on_event("startup")
def load_engine():
    global engine
    engine = SearchEngine()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.get("/")
def root():
    return {"status": "NyaayaSearch API is running"}


@app.post("/search")
def search(request: SearchRequest):
    results = engine.search(request.query, top_k=request.top_k)
    return {"query": request.query, "results": results}


@app.post("/explain")
def explain(request: SearchRequest):
    results = engine.search(request.query, top_k=request.top_k)
    explanation = generate_explanation(request.query, results)
    return {
        "query": request.query,
        "results": results,
        "explanation": explanation,
    }
