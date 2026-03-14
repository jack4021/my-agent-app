"""Chainlit web application for the agent.

This module provides the chat interface for interacting with the agent,
handling message events and displaying responses.
"""

import asyncio
import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from agent import create_agent, run_agent
from logging_config import logger

DB_PATH = "/app/data/chainlit.db"


async def init_db():
    """Initialize SQLite database with required tables."""
    import aiosqlite

    logger.info("Initializing SQLite database...")
    # noinspection SqlNoDataSourceInspection
    schema = ("\n"
              "CREATE TABLE IF NOT EXISTS users\n"
              "(\n"
              "    \"id\"         TEXT PRIMARY KEY,\n"
              "    \"identifier\" TEXT NOT NULL UNIQUE,\n"
              "    \"metadata\"   TEXT NOT NULL,\n"
              "    \"createdAt\"  TEXT\n"
              ");\n"
              "\n"
              "CREATE TABLE IF NOT EXISTS threads\n"
              "(\n"
              "    \"id\"             TEXT PRIMARY KEY,\n"
              "    \"createdAt\"      TEXT,\n"
              "    \"name\"           TEXT,\n"
              "    \"userId\"         TEXT,\n"
              "    \"userIdentifier\" TEXT,\n"
              "    \"tags\"           TEXT,\n"
              "    \"metadata\"       TEXT,\n"
              "    FOREIGN KEY (\"userId\") REFERENCES users (\"id\") ON DELETE CASCADE\n"
              ");\n"
              "\n"
              "CREATE TABLE IF NOT EXISTS steps\n"
              "(\n"
              "    \"id\"            TEXT PRIMARY KEY,\n"
              "    \"name\"          TEXT    NOT NULL,\n"
              "    \"type\"          TEXT    NOT NULL,\n"
              "    \"threadId\"      TEXT    NOT NULL,\n"
              "    \"parentId\"      TEXT,\n"
              "    \"streaming\"     INTEGER NOT NULL,\n"
              "    \"waitForAnswer\" INTEGER,\n"
              "    \"isError\"       INTEGER,\n"
              "    \"metadata\"      TEXT,\n"
              "    \"tags\"          TEXT,\n"
              "    \"input\"         TEXT,\n"
              "    \"output\"        TEXT,\n"
              "    \"createdAt\"     TEXT,\n"
              "    \"command\"       TEXT,\n"
              "    \"start\"         TEXT,\n"
              "    \"end\"           TEXT,\n"
              "    \"generation\"    TEXT,\n"
              "    \"showInput\"     TEXT,\n"
              "    \"language\"      TEXT,\n"
              "    \"indent\"        INTEGER,\n"
              "    \"defaultOpen\"   INTEGER,\n"
              "    \"autoCollapse\"  INTEGER,\n"
              "    FOREIGN KEY (\"threadId\") REFERENCES threads (\"id\") ON DELETE CASCADE\n"
              ");\n"
              "\n"
              "CREATE TABLE IF NOT EXISTS elements\n"
              "(\n"
              "    \"id\"          TEXT PRIMARY KEY,\n"
              "    \"threadId\"    TEXT,\n"
              "    \"type\"        TEXT,\n"
              "    \"url\"         TEXT,\n"
              "    \"chainlitKey\" TEXT,\n"
              "    \"name\"        TEXT NOT NULL,\n"
              "    \"display\"     TEXT,\n"
              "    \"objectKey\"   TEXT,\n"
              "    \"size\"        TEXT,\n"
              "    \"page\"        INTEGER,\n"
              "    \"language\"    TEXT,\n"
              "    \"forId\"       TEXT,\n"
              "    \"mime\"        TEXT,\n"
              "    \"props\"       TEXT,\n"
              "    FOREIGN KEY (\"threadId\") REFERENCES threads (\"id\") ON DELETE CASCADE\n"
              ");\n"
              "\n"
              "CREATE TABLE IF NOT EXISTS feedbacks\n"
              "(\n"
              "    \"id\"       TEXT PRIMARY KEY,\n"
              "    \"forId\"    TEXT    NOT NULL,\n"
              "    \"threadId\" TEXT    NOT NULL,\n"
              "    \"value\"    INTEGER NOT NULL,\n"
              "    \"comment\"  TEXT,\n"
              "    FOREIGN KEY (\"threadId\") REFERENCES threads (\"id\") ON DELETE CASCADE\n"
              ");\n")

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
    return SQLAlchemyDataLayer(conninfo="sqlite+aiosqlite:////app/data/chainlit.db")


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
