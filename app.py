"""Chainlit web application for the agent.

This module provides the chat interface for interacting with the agent,
handling message events and displaying responses.
"""

import asyncio
from pathlib import Path

import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from agent import create_agent, run_agent
from logging_config import logger

DB_PATH = "./data/chainlit.db"
SCHEMA_PATH = Path(__file__).parent / "sql" / "schema.sql"


async def init_db():
    """Initialize SQLite database with required tables."""
    import aiosqlite

    logger.info("Initializing SQLite database...")
    schema = SCHEMA_PATH.read_text()

    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(schema)
        await db.commit()
    logger.info(f"Database initialized at {DB_PATH}")


@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    return None


@cl.data_layer
def get_data_layer():
    asyncio.get_event_loop().run_until_complete(init_db())
    return SQLAlchemyDataLayer(conninfo="sqlite+aiosqlite:///data/chainlit.db")


# Initialize agent once
agent = create_agent()


@cl.on_chat_resume
async def on_chat_resume(thread):
    pass


@cl.on_chat_start
async def start_chat():
    """Handle chat session initialization."""
    logger.info("Chainlit chat started")


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming user messages and send agent responses.

    Args:
        message: The incoming Chainlit message object containing user input.
    """
    config = {"configurable": {"thread_id": message.thread_id}}
    user_input = str(message.content)
    response = run_agent(user_input, agent, config)
    await cl.Message(content=response).send()
