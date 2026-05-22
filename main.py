import os
import json
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

load_dotenv()
import logging
logging.basicConfig(level=logging.INFO)
logging.info(f"GEMINI_API_KEY configured: {bool(os.getenv('GEMINI_API_KEY'))}")
logging.info(f"OPENROUTER_API_KEY configured: {bool(os.getenv('OPENROUTER_API_KEY'))}")

# Global LLM provider config (can be toggled at runtime)
LLM_PROVIDER = {
    "use_openrouter": bool(os.getenv("OPENROUTER_API_KEY")),
    "openrouter_model": os.getenv("OPENROUTER_MODEL", "google/gemma-3-27b-it:free"),
}

# Load Bible data
BASE_DIR = os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, "bible_data", "book_metadata.json"), encoding="utf-8") as f:
    BOOK_METADATA = json.load(f)
with open(os.path.join(BASE_DIR, "bible_data", "strongs_sample.json"), encoding="utf-8") as f:
    STRONGS_DATA = json.load(f)

BIBLE_API     = os.getenv("BIBLE_API_BASE", "https://bible-api.com")
GEMINI_MODEL  = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[OK] Lumina Bible Interpreter starting — model: {GEMINI_MODEL}")
    
    # ── RAG Auto-Indexing ──
    from rag.knowledge_base import KnowledgeBase
    kb = KnowledgeBase()
    if not kb.is_indexed():
        print("[*] Knowledge Base not found or incomplete. Starting auto-indexing...")
        kb.index_all()
    else:
        print("[+] Knowledge Base is ready.")
        
    yield
    print("[STOP] Lumina Bible Interpreter shutting down.")


app = FastAPI(title="Lumina Bible Interpreter", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Pydantic models ───────────────────────────────────────────

class InterpretRequest(BaseModel):
    reference: str
    task_type: str = "interpretation"
    translation: str = "kjv"
    focus_terms: List[str] = []
    depth: str = "full"


class QueryRequest(BaseModel):
    raw_query: str
    default_translation: str = "kjv"


# ─── API Routes ────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    try:
        from rag.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        kb_status = "ready" if kb.is_indexed() else "indexing_required"

        return {
            "status": "ok",
            "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY")),
            "openrouter_api_configured": bool(os.getenv("OPENROUTER_API_KEY")),
            "llm_provider": "openrouter" if LLM_PROVIDER["use_openrouter"] else "gemini",
            "active_model": LLM_PROVIDER["openrouter_model"] if LLM_PROVIDER["use_openrouter"] else GEMINI_MODEL,
            "kb_status": kb_status,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/openrouter/models")
async def openrouter_free_models():
    """List all free models available on OpenRouter."""
    from agents.base_agent import BaseAgent
    return await BaseAgent.list_free_models()


class SetModelRequest(BaseModel):
    model_id: str
    use_openrouter: bool = True


@app.post("/api/openrouter/set-model")
async def set_openrouter_model(req: SetModelRequest):
    """Switch the active LLM model at runtime."""
    LLM_PROVIDER["use_openrouter"] = req.use_openrouter
    if req.use_openrouter:
        LLM_PROVIDER["openrouter_model"] = req.model_id
        os.environ["OPENROUTER_MODEL"] = req.model_id
    logging.info(f"LLM provider switched: openrouter={req.use_openrouter}, model={req.model_id}")
    return {
        "status": "ok",
        "llm_provider": "openrouter" if req.use_openrouter else "gemini",
        "active_model": req.model_id,
    }


@app.get("/api/books")
async def get_books():
    return BOOK_METADATA


@app.get("/api/chapter")
async def get_chapter(
    book: str = Query(...),
    chapter: int = Query(...),
    version: str = Query("kjv"),
):
    ref = f"{book}+{chapter}"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(f"{BIBLE_API}/{ref}?translation={version}")
            if r.status_code != 200:
                raise HTTPException(status_code=r.status_code, detail="Bible API error")
            return r.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Bible API timeout")


@app.get("/api/verse")
async def get_verse(
    book: str = Query(...),
    chapter: int = Query(...),
    verse: int = Query(...),
    version: str = Query("kjv"),
):
    ref = f"{book}+{chapter}:{verse}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(f"{BIBLE_API}/{ref}?translation={version}")
            if r.status_code != 200:
                raise HTTPException(status_code=r.status_code, detail="Bible API error")
            return r.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Bible API timeout")


@app.post("/api/parse-query")
async def parse_query(request: QueryRequest):
    from agents.intake_agent import IntakeAgent
    agent = IntakeAgent(use_openrouter=LLM_PROVIDER["use_openrouter"])
    if LLM_PROVIDER["use_openrouter"]:
        agent.openrouter_model = LLM_PROVIDER["openrouter_model"]
    return await agent.process(request.raw_query, request.default_translation)


@app.post("/api/interpret")
async def interpret(request: InterpretRequest):
    from agents.orchestrator_agent import OrchestratorAgent
    orchestrator = OrchestratorAgent(
        strongs_data=STRONGS_DATA,
        book_metadata=BOOK_METADATA,
        use_openrouter=LLM_PROVIDER["use_openrouter"],
        openrouter_model=LLM_PROVIDER["openrouter_model"],
    )
    result = await orchestrator.run(
        reference=request.reference,
        task_type=request.task_type,
        translation=request.translation,
        focus_terms=request.focus_terms,
        depth=request.depth,
    )
    return JSONResponse(content=result)


@app.get("/api/rag/related")
async def get_rag_related(reference: str = Query(...), testament: str = Query("NT")):
    from rag import RAGRetriever
    retriever = RAGRetriever()
    context = retriever.get_context_bundle(reference, testament)
    return context


# ─── Serve frontend ────────────────────────────────────────────
app.mount(
    "/",
    StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True),
    name="static",
)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
