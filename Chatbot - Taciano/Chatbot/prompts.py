from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import AI_CONTEXTUALIZE_PROMPT, AI_SYSTEM_PROMPT


# Contexto
contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system", AI_CONTEXTUALIZE_PROMPT), # Prompt de contexto da IA
        MessagesPlaceholder("chat_history"), # Placeholder para o histórico de mensagens
        ("human", "{input}"),  # Mensagem do usuário
])

# Prompt do sistema, que vai buscar as informações no banco de dados
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", AI_SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"), # Placeholder para o histórico de mensagens
    ("human", "{input}"),  # Mensagem do usuário
])