from dotenv import load_dotenv
from langchain.agents import create_agent



from config import config
from llm.factory import get_llm
from memory.short_term_memory import get_summarization_middleware
from observability import logger

from agent.prompts import system_prompt

# from agent.prompts.system_prompts import SYSTEM_PROMPT

from mcp_intigration import get_mcp_client


#from tools import tools

load_dotenv()


async def build_agent(checkpoint):
    """
    Build and return a LangGraph ReAct agent with
    summarization middleware and MCP tools.
    """

    logger.info("Loading configuration...")

    _ = config

    mcp_client = get_mcp_client()

    mcp_tools = await mcp_client.get_tools()

    logger.info("Loaded %d MCP tools.", len(mcp_tools))

    logger.info("Initializing LLM...")

    llm = get_llm()

    # system_prompt = SYSTEM_PROMPT
    # Bind tools to LLM
    # llm_with_tools = llm.bind_tools(mcp_tools, search_logs)

    tools = [
        *mcp_tools
    ]


    logger.info("Creating summarization middleware...")

    middleware = get_summarization_middleware(llm=llm)

    logger.info("Crypto AI agent creating...")

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        middleware=[middleware],
        checkpointer=checkpoint,
    )

    logger.info("Crypto AI agent created successfully")

    return agent