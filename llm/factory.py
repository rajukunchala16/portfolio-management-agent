from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from config import config


def get_llm():
    provider = config["llm"]["provider"].lower()
    model=config["llm"]["model"].lower()

    if provider == "openai":
        return ChatOpenAI(
            model_name=model,
        )

    elif provider == "anthropic":
        return ChatAnthropic(
            model=model,
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")


def get_embedder():
    provider = config["embeddings"]["provider"].lower()
    model = config["embeddings"]["model"].lower()

    if provider == "openai":
        return OpenAIEmbeddings(
            model=model
        )

    elif provider == "huggingface":
        return HuggingFaceEmbeddings(
            model_name=model
        )

    raise ValueError(f"Unsupported embedding provider: {provider}")