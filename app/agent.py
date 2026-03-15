"""Agent creation and execution utilities.

This module provides functions to create a deep agent with file system,
web search, and browsing capabilities. It supports both Redis-backed
and in-memory storage/checkpointing.
"""

from deepagents import create_deep_agent
from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.redis import RedisStore
from langgraph.store.memory import InMemoryStore
from pathlib import Path

# noinspection PyPackageRequirements
from redis import Redis
from deepagents.backends import (
    CompositeBackend,
    FilesystemBackend,
    StoreBackend,
)
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from tools import get_tools
from logging_config import logger

load_dotenv()

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "system.md").read_text()


def create_agent():
    """Create and configure the deep agent with tools and storage backends.

    Sets up a composite backend for file system access, initializes the model,
    and configures either Redis-based or in-memory storage and checkpointing
    depending on Redis availability.

    Returns:
        The configured deep agent instance with tools and system prompt.
    """
    backend = lambda rt: CompositeBackend(
        default=StoreBackend(rt),
        routes={"/": FilesystemBackend(root_dir="workspace", virtual_mode=True)},
    )

    # Use in-memory storage by default
    store = InMemoryStore()
    checkpointer = InMemorySaver()

    # Attempt to use Redis for persistent storage if available
    try:
        client = Redis.from_url("redis://redis:6379")
        client.ping()  # Verify connection
        store = RedisStore(conn=client)
        checkpointer = RedisSaver(redis_client=client)
        checkpointer.setup()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed, using in-memory store and saver: {e}")

    return create_deep_agent(
        model=ChatOpenRouter(model="x-ai/grok-4.1-fast"),
        store=store,
        checkpointer=checkpointer,
        backend=backend,
        system_prompt=SYSTEM_PROMPT,
        tools=get_tools(),
    )


def run_agent(prompt: str, agent, config: dict) -> str:
    """Execute the agent with a user prompt and return the response.

    Args:
        prompt: The user input message to process.
        agent: The pre-configured agent instance.
        config: Configuration dictionary containing thread_id for checkpointing.

    Returns:
        The agent's response content as a string, or an error message.
    """
    logger.info(f"User prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content=prompt)]}, config=config
        )
        response = result["messages"][-1].content
        logger.info(f"Agent response: {len(response)}")
        return response
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return f"Error: {str(e)}"
