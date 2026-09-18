from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from search_core import SearchEngine
from rag_core import generate_explanation, translate_to_english
from citations_core import find_related_cases

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


def attach_related_cases(results):
    for r in results:
        try:
            r["related_cases"] = find_related_cases(r["act_name"], r["section_number"])
        except Exception:
            r["related_cases"] = []
    return results


@app.get("/")
def root():
    return {"status": "NyaayaSearch API is running"}


@app.post("/search")
def search(request: SearchRequest):
    results = engine.search(request.query, top_k=request.top_k)
    results = attach_related_cases(results)
    return {"query": request.query, "results": results}


@app.post("/explain")
def explain(request: SearchRequest):
    search_query = translate_to_english(request.query)
    results = engine.search(search_query, top_k=request.top_k)
    results = attach_related_cases(results)
    explanation = generate_explanation(request.query, results)
    return {
        "query": request.query,
        "translated_query": search_query,
        "results": results,
        "explanation": explanation,
    }
