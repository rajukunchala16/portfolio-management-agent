from pathlib import Path

import aiosqlite
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from config import config
from memory.session import Session


def get_checkpoint_path(session: Session) -> Path:

    return session.path / config["memory"]["checkpoint_db"]


async def get_checkpoint(session: Session):

    db = await aiosqlite.connect(
        get_checkpoint_path(session)
    )

    return AsyncSqliteSaver(db)


def get_summarization_middleware(llm):

    return SummarizationMiddleware(
        model=llm,
        max_tokens_before_summary=3000,
        messages_to_keep=10,
    )