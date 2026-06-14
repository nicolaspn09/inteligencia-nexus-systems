from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
from langchain_core.caches import BaseCache
from config import GROQ_MODEL, GROQ_TEMPERATURE, GROQ_API_KEY
from vectorstore import get_vectorstore
from prompts import contextualize_prompt, qa_prompt
from memory import get_session_history


def get_rag_chain():
    # Adiciona a chamada para rebuild do modelo Pydantic
    ChatGroq.model_rebuild()

    llm = ChatGroq(
        model=GROQ_MODEL,
        api_key=str(GROQ_API_KEY),
    )

    print(f"Iniciando a busca no vectorstore")
    # Pega o banco de dados vetorizado e faz uma busca dos dados
    retriever = get_vectorstore().as_retriever()
    print(f"Obteve os dados de vectorstore")
    # Cria o histórico de mensagens para a IA, relevantes para o contexto da conversa
    history_aware_chain = create_history_aware_retriever(llm, retriever, contextualize_prompt) 
    # Cria o chain de perguntas e respostas, que vai buscar as informações no banco de dados para o contexto da conversa
    question_answer_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=qa_prompt,
    )

    print(f"[GROQ] Modelo: {GROQ_MODEL}, API Key (primeiros 5 chars): {str(GROQ_API_KEY)[:5]}*****") # Ajuda a verificar se a chave está sendo lida.

    return create_retrieval_chain(history_aware_chain, question_answer_chain)

def get_conversational_rag_chain():
    # Cria o chain de perguntas e respostas, que vai buscar as informações no banco de dados para o contexto da conversa
    rag_chain = get_rag_chain()
    
    return RunnableWithMessageHistory(
        # Cria o chain de perguntas e respostas, que vai buscar as informações no banco de dados para o contexto da conversa
        runnable=rag_chain,
         # Cria o histórico de mensagens para a IA, relevantes para o contexto da conversa
        get_session_history=get_session_history,
        # Informa os parâmetros de entrada e saída do chain 
        input_message_key="input",
        # Informa o histórico de mensagens da conversa
        history_messages_key="chat_history",
        # Informa a mensagem de saída do chain, que vai ser a resposta da IA
        output_message_key="answer",
    )