from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from config import FRONTEND_URL
from rag import init_rag, get_collection_size
from agent import run_agent
from escalation import log_query, log_escalation, get_analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Initialising RAG — embedding KB documents...")
    init_rag()
    print("[Startup] RAG ready.")
    yield


app = FastAPI(title="Support Deflection Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post("/chat")
async def chat(req: ChatRequest):
    result = run_agent(req.session_id, req.message)

    log_query(
        session_id=req.session_id,
        intent=result["intent"],
        tier=result["tier"],
        confidence=result["confidence_score"],
        escalated=result["escalated"],
    )

    if result["escalated"]:
        log_escalation(
            session_id=req.session_id,
            intent=result["intent"],
            reason=result["escalation_reason"],
            query=req.message,
        )

    return {**result, "session_id": req.session_id}


@app.get("/health")
async def health():
    size = get_collection_size()
    return {
        "status": "ok",
        "kb_doc_count": 5,
        "chroma_collection_size": size,
    }


@app.get("/analytics")
async def analytics():
    return get_analytics()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
