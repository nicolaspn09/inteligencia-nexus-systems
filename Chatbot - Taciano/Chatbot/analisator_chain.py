from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from config import GROQ_MODEL, GROQ_TEMPERATURE, GROQ_API_KEY


def get_message_introduction(message):
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
    # Modelo mais robusto
    model = ChatGroq(
        model=GROQ_MODEL
        )

    messages = [
        {"role": "system", "content": "Você é um agente responsável por analisar a mensagem do usuário e me retornar se foi uma mensagem de contato inicial ou não. Se for uma mensagem de contato inicial, retorne 'sim', caso contrário, retorne 'não'. Se for uma mensagem para sair, retorne 'sair'."},
        {"role": "user", "content": f"{message}"},
    ]

    return model.invoke(messages)