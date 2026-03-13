import chainlit as cl
from agent import create_agent, run_agent

# Initialize agent once
agent = create_agent()
thread_id = "default"
config = {"configurable": {"thread_id": thread_id}}


@cl.on_chat_start
async def start_chat():
    pass


@cl.on_message
async def main(message: cl.Message):
    user_input = message.content
    response = run_agent(user_input, agent, config)
    await cl.Message(content=response).send()
