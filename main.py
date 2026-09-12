import asyncio

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from config import config
from llm.factory import get_llm
from observability import logger
from agent.factory import build_agent


from agent.orchestrator import handle_query
console = Console()

from memory.session import SessionManager
from memory.short_term_memory import get_checkpoint
from agent.factory import build_agent

 # Load environment variables
load_dotenv()



async def main():
    logger.info("Application started")
    logger.info("Configuration loaded")

    llm = get_llm()
    logger.info("LLM initialized")

    logger.info("Initializing session manager")

    session_manager = SessionManager()

    session = session_manager.create()

    logger.info(
        "Created session: %s (%s)",
        session.name,
        session.id,
    )

    checkpoint = await get_checkpoint(session)

    logger.info("Checkpoint initialized")

    agent = await build_agent(
        checkpoint=checkpoint
    )

    thread_config = {
        "configurable": {
            "thread_id": session.id,
        }
    }

    logger.info(
        "Agent initialized for session %s",
        session.id,
    )
   
    console.print(
        Panel.fit(
            "[bold cyan]AI Assistant[/bold cyan]\n\n"
            "Commands:\n"
            "• /ask <question>\n"
            "• exit",
            title="Welcome",
        )
    )
    
    while True:
        try:
            user_input = Prompt.ask(
                "[bold green]>[/bold green]"
            ).strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                logger.info("Application terminated by user")
                console.print(
                    "[bold yellow]Goodbye! 👋[/bold yellow]"
                )
                break

            if not user_input.startswith("/ask"):
                console.print(
                    "[bold red]Invalid command.[/bold red] "
                    "Use [cyan]/ask <question>[/cyan]"
                )
                continue

            question = user_input[4:].strip()

            if not question:
                console.print(
                    "[yellow]Please enter a question.[/yellow]"
                )
                continue

            logger.info("Question: %s", question)

            with console.status(
                "[bold cyan]Thinking...[/bold cyan]",
                spinner="dots",
            ):
                logger.debug(
                    "Invoking LangGraph agent "
                    "(thread_id=%s)",
                    session.id,
                )

                result =  await handle_query(
                            agent=agent,
                            question=user_input,
                            thread_id=session.id,
                )

            answer = result

            logger.info("Answer generated successfully")

            console.print("\n[bold blue]AI:[/bold blue]")
            console.print(answer)
            console.print()

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received")
            console.print(
                "\n[yellow]Exiting...[/yellow]"
            )
            break

        except Exception:
            logger.exception(
                "Unexpected error while processing request"
            )

            console.print(
                "[bold red]An unexpected error occurred.[/bold red]"
            )

    
if __name__ == "__main__":
    asyncio.run(main())