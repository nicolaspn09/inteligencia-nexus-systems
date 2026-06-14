import os
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

from mcp_server import MCP_SERVERS_CONFIG

load_dotenv()


async def main():
    model = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", api_key = 'DADO_HIGIENIZADO')
    memory = MemorySaver()
    
    print(MCP_SERVERS_CONFIG)
    mcp_client = MultiServerMCPClient(MCP_SERVERS_CONFIG)
    tools = await mcp_client.get_tools()

    system_message = '''
    Você é um agente que controla a agenda do usuário. Use suas ferramentas para responder as perguntas do usuário.
    '''

    agent_executor = create_react_agent(
        model=model,
        tools=tools,
        prompt=system_message,
        checkpointer=memory,
    )

    config = {'configurable': {'thread_id': '1'}}

    while True:
        input_message = {
            'role': 'user',
            'content': input('Digite: '),
        }
        async for step in agent_executor.astream(
            {'messages': [input_message]}, config, stream_mode='values'
        ):
            step['messages'][-1].pretty_print()


asyncio.run(main())
