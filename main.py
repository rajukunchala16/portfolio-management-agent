"""FastAPI entrypoint for the portfolio management agent."""

import asyncio
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.factory import build_agent
from agent.orchestrator import handle_query
from llm.factory import get_llm
from memory.session import SessionManager
from memory.short_term_memory import get_checkpoint
from observability import logger

load_dotenv()


class QuestionRequest(BaseModel):
    """Request model for a portfolio question."""

    question: str


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize the LangGraph agent once when the FastAPI app starts."""
    logger.info("Application started")
    logger.info("Configuration loaded")

    _ = get_llm()
    logger.info("LLM initialized")

    session_manager = SessionManager()
    session = session_manager.create()
    logger.info("Created session: %s (%s)", session.name, session.id)

    checkpoint = await get_checkpoint(session)
    logger.info("Checkpoint initialized")

    agent = await build_agent(checkpoint=checkpoint)
    logger.info("Agent initialized for session %s", session.id)

    _app.state.agent = agent
    _app.state.session_id = session.id

    yield


app = FastAPI(title="Portfolio Management Agent", lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "message": "Portfolio management agent is running",
        "session_id": getattr(app.state, "session_id", "unknown"),
    }


@app.post("/ask")
async def ask_question(payload: QuestionRequest) -> dict[str, str]:
    """Accept a user question and return the agent answer."""
    question = payload.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    agent = getattr(app.state, "agent", None)
    session_id = getattr(app.state, "session_id", "default")

    if agent is None:
        raise HTTPException(status_code=500, detail="Agent is not initialized.")

    logger.info("Question: %s", question)

    answer = await handle_query(
        agent=agent,
        question=question,
        thread_id=session_id,
    )

    return {"answer": answer, "session_id": session_id}


async def main() -> None:
    """Compatibility entrypoint for local development."""
    logger.info("Use uvicorn main:app --reload to run the FastAPI service.")


if __name__ == "__main__":
    asyncio.run(main())
