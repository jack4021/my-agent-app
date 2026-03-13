from deepagents import create_deep_agent
from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.redis import RedisStore
from langgraph.store.memory import InMemoryStore
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

SYSTEM_PROMPT = """
You are a helpful assistant with access to file system tools, web search, and browsing capabilities.
""".strip()


def create_agent():
    backend = lambda rt: CompositeBackend(
        default=StoreBackend(rt),
        routes={"/": FilesystemBackend(root_dir="workspace", virtual_mode=True)},
    )

    # Default to in-memory
    store = InMemoryStore()
    checkpointer = InMemorySaver()

    # Try Redis if available
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
    logger.info(f"User prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content=prompt)]}, config=config
        )
        response = result["messages"][-1].content
        logger.info(
            f"Agent response: {response[:100]}{'...' if len(response) > 100 else ''}"
        )
        return response
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return f"Error: {str(e)}"
