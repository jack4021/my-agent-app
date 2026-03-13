"""Chainlit web application for the agent.

This module provides the chat interface for interacting with the agent,
handling message events and displaying responses.
"""

import chainlit as cl
from agent import create_agent, run_agent
from logging_config import logger

# Initialize agent once
agent = create_agent()
thread_id = "default"
config = {"configurable": {"thread_id": thread_id}}


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
    user_input = str(message.content)
    response = run_agent(user_input, agent, config)
    await cl.Message(content=response).send()
