"""Deployment-ready API server for the ai-banking-advisory-agent equipment financing agent."""

import logging
import os
import time
import uuid
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from adaptive_agent import EquipmentFinancingAdaptiveAgent

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

LOG_DIR = BASE_DIR / "outputs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "deploy.log"

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_PATH, encoding="utf-8")
    ]
)
logger = logging.getLogger("deploy_server")

app = FastAPI(
    title="ai-banking-advisory-agent Equipment Financing Agent API",
    description="Deployment-ready API for the ai-banking-advisory-agent equipment financing agent with tracing and graceful failure handling.",
    version="0.1.0"
)

SESSION_AGENTS: Dict[str, EquipmentFinancingAdaptiveAgent] = {}
HEALTH_AGENT: Optional[EquipmentFinancingAdaptiveAgent] = None


def get_health_agent() -> EquipmentFinancingAdaptiveAgent:
    global HEALTH_AGENT
    if HEALTH_AGENT is None:
        HEALTH_AGENT = create_agent()
    return HEALTH_AGENT


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    query: str
    response: str
    rating: int
    comments: str = ""
    session_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    ready: bool
    rag_retrieval_active: bool
    retriever_available: bool


START_TIME = time.time()


def create_agent() -> EquipmentFinancingAdaptiveAgent:
    return EquipmentFinancingAdaptiveAgent(
        kb_path=str(DATA_DIR / "knowledge_base.json"),
        retriever_db_path=str(DATA_DIR / "chroma_db"),
        max_tool_calls=4,
        short_term_capacity=10
    )


def get_agent(session_id: Optional[str]) -> (str, EquipmentFinancingAdaptiveAgent):
    if session_id and session_id in SESSION_AGENTS:
        return session_id, SESSION_AGENTS[session_id]

    new_session_id = session_id or uuid.uuid4().hex
    agent = create_agent()
    SESSION_AGENTS[new_session_id] = agent
    logger.info(f"Created new session {new_session_id}")
    return new_session_id, agent


@app.middleware("http")
async def add_tracing(request: Request, call_next):
    trace_id = uuid.uuid4().hex[:8]
    request.state.trace_id = trace_id
    start_time = time.monotonic()
    response = await call_next(request)
    duration_ms = (time.monotonic() - start_time) * 1000
    logger.info(
        f"trace={trace_id} method={request.method} path={request.url.path} status={response.status_code} duration_ms={duration_ms:.1f}"
    )
    return response


@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", "unknown")
    logger.exception(f"Internal error trace={trace_id}")
    content = {
        "trace_id": trace_id,
        "error": "An internal error occurred. Please try again later.",
        "details": "See server logs for trace details."
    }
    return JSONResponse(status_code=500, content=content)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    uptime = time.time() - START_TIME
    try:
        health_agent = get_health_agent()
        retriever_available = getattr(health_agent, "retriever", None) is not None
        rag_retrieval_active = retriever_available and getattr(health_agent.retriever, "vector_store", None) is not None
    except Exception:
        retriever_available = False
        rag_retrieval_active = False

    return HealthResponse(
        status="ok",
        uptime_seconds=round(uptime, 2),
        ready=True,
        rag_retrieval_active=rag_retrieval_active,
        retriever_available=retriever_available
    )


@app.post("/query")
async def query_endpoint(payload: QueryRequest, request: Request):
    trace_id = request.state.trace_id
    session_id, agent = get_agent(payload.session_id)
    start_time = time.monotonic()

    try:
        result = agent.process_query(payload.query)
    except Exception as exc:
        logger.exception(f"Query processing failed trace={trace_id}")
        raise HTTPException(status_code=500, detail="Failed to process query.")

    latency_ms = round((time.monotonic() - start_time) * 1000, 2)
    response = {
        "trace_id": trace_id,
        "session_id": session_id,
        "latency_ms": latency_ms,
        "result": result
    }
    logger.info(f"Processed query trace={trace_id} session={session_id} latency_ms={latency_ms}")
    return response


@app.post("/feedback")
async def feedback_endpoint(payload: FeedbackRequest, request: Request):
    trace_id = request.state.trace_id
    session_id, agent = get_agent(payload.session_id)

    try:
        feedback = agent.collect_feedback(
            query=payload.query,
            response=payload.response,
            rating=payload.rating,
            comments=payload.comments
        )
    except ValueError as exc:
        logger.warning(f"Invalid feedback trace={trace_id} error={exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        logger.exception(f"Feedback processing failed trace={trace_id}")
        raise HTTPException(status_code=500, detail="Failed to store feedback.")

    logger.info(f"Stored feedback trace={trace_id} session={session_id} rating={payload.rating}")
    return {"trace_id": trace_id, "session_id": session_id, "feedback": feedback}


@app.get("/adaptation")
async def adaptation_endpoint(session_id: Optional[str] = None):
    session_id, agent = get_agent(session_id)
    summary = agent.feedback_manager.get_feedback_summary()
    explanation = agent.explain_adaptation()
    return {
        "session_id": session_id,
        "feedback_summary": summary,
        "adaptation_explanation": explanation
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting deployment-ready ai-banking-advisory-agent API server")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level=os.getenv("LOG_LEVEL", "info"))

