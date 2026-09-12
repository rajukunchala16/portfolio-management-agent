"""
Agent Orchestrator

Responsibilities
----------------
1. Accept user query
2. Invoke LangGraph agent
3. Return final response
4. Handle errors
"""

from __future__ import annotations

from typing import Any

from observability import logger


class Orchestrator:
    """
    Handles execution of user queries.
    """

    def __init__(self):
        self.logger = logger

    async def handle_query(
        self,
        agent: Any,
        question: str,
        thread_id: str = "default",
    ) -> str:
        """
        Execute a user query using the LangGraph agent.

        Args:
            agent: LangGraph compiled agent.
            question: User input.
            thread_id: Conversation/session id.

        Returns:
            Assistant response.
        """

        try:
            self.logger.info("=" * 80)
            self.logger.info("Received User Query")
            self.logger.info("Question : %s", question)

            result = await agent.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": question,
                        }
                    ]
                },
                config={
                    "configurable": {
                        "thread_id": thread_id,
                    }
                },
            )

            messages = result.get("messages", [])

            if not messages:
                self.logger.warning("No response returned from agent.")
                return "I couldn't generate a response."

            response = messages[-1].content

            self.logger.info("Agent response generated successfully.")
            self.logger.info("=" * 80)

            return response

        except Exception:
            self.logger.exception("Error while processing query.")
            return (
                "Sorry, an unexpected error occurred while processing "
                "your request."
            )


# ---------------------------------------------------------
# Singleton Instance
# ---------------------------------------------------------

orchestrator = Orchestrator()


# ---------------------------------------------------------
# Public Function
# ---------------------------------------------------------

async def handle_query(
    agent: Any,
    question: str,
    thread_id: str = "default",
) -> str:
    """
    Public entry point called from main.py.
    """

    return await orchestrator.handle_query(
        agent=agent,
        question=question,
        thread_id=thread_id,
    )