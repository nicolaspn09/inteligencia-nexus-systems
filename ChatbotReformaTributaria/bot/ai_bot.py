import os
from decouple import config # Busca a variável de ambiente
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq # Busca os modelos do groq
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings
import psycopg2
from dotenv import load_dotenv

# Comunica com o groq
os.environ["GROQ_API_KEY"] = config("GROQ_API_KEY")

# Classe do bot
class AIBot():    
    # Inicializador
    def __init__(self):
        # Cria o modelo do Groq
        self.__chat = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")
        # Cria um retriever, uma instância do banco de dadosd
        self.__retriever = self.__build_retriever()

    # Roda query para executar o PG
    def conecta_pg(sql):
        """
        Roda query para executar

        Parameters:
        Sql = string

        Returns:
        tabela_sql = datatable
        """

        # Carrega as variáveis do ambiente
        load_dotenv()

        host_database = os.getenv("HOST")
        database_database = os.getenv("DATABASE")
        user_database = os.getenv("USER_PG")
        password_database = os.getenv("PASSWORD")

        host = host_database # Endereço do servidor
        database = database_database  # Nome do banco de dados
        user = user_database  # Nome de usuário para acessar o banco de dados
        password = password_database  # Senha do usuário para acessar o banco de dados
        port = 5433

        # Estabelece a conexão com o banco de dados
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )

        cursor = connection.cursor()
        cursor.execute(sql)
        tabela_sql = cursor.fetchall()
        cursor.close()
        connection.close()

        # Retorna o resultado da consulta do SQL para o usuário
        return tabela_sql

    # Localiza o banco de dados e busca as informações conforme o prompt
    def __build_retriever(self):
        # Informa o local do banco de dados
        persist_directory = "/ChatBotWhatsEvolution/chroma_data"
        # Busca as informações relevantes
        embedding = HuggingFaceEmbeddings()

        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding,
        )

        return vector_store.as_retriever(
            search_kwargs={"k": 30}, # Busca até 30 resultados no máximo
        )

    def __build_messages(self, history_messages, question):
        # Garantir que history_messages não seja None
        if history_messages is None:
            history_messages = []

        messages = []

        # Construir a lista de mensagens a partir do histórico
        for message in history_messages:
            if isinstance(message, dict):  # Verifica se message é um dicionário
                message_class = HumanMessage if message.get("fromMe") else AIMessage
                messages.append(message_class(content=message.get("body", "")))
            elif isinstance(message, str):  # Se for uma string, trata como mensagem do usuário
                messages.append(HumanMessage(content=message))
            else:
                raise ValueError(f"Tipo de mensagem inesperado: {type(message)}")

        # Adiciona a mensagem atual (pergunta)
        messages.append(HumanMessage(content=question))

        return messages

    # Recebe a mensagem do usuário e processa a partir de um prompt
    def invoke(self, history_messages, question):
        SYSTEM_TEMPLATE = """
        Você é um assistente virtual, de uma professora de Inglês. Seu objetivo é ajudar os usuários com perguntas sobre a língua inglesa. Responda com base no contexto a seguir.
        Responda de forma natural, agradável e respeitosa. Seja objetivo nas respostas, com informações claras e diretas. Foque em ser natural e humanizado, como um diálogo comum entre duas pessoas.
        Leve em consideração também o histórico de mensagens de conversa com o usuário.
        Não seja grosseiro com as pessoas, sempre seja educado.

        Quando for a primeira mensagem do usuário ou você identificar que é um sinal de entrada, como "bom dia", "boa tarde", "oi", "olá", "hello", use a seguinte mensagem de retorno:
        
        [
        🎉 Hello there! Bem-vindo(a) ao SuyYourWay! 🌟

        Prepare-se para aprender inglês de um jeito tão legal que até o dicionário vai querer participar! 📚💃

        Aqui, você não vai só aprender inglês, vai viver o inglês — com muitas risadas, dicas práticas e até uns "oops" no caminho (quem nunca, né?).

        Então, bora embarcar nessa jornada fluente? Porque aqui, Your Way é sempre o melhor caminho! 😉
        ]

        Caso não seja uma mensagem de boas vindas da pessoa, use sua base de conhecimento para conversar, não envie novamente a mensagem de boas vindas que está descrita entre os colchetes.
        Interprete as mensagens para você entender o contexto completo, mas responda apenas a última mensagem feita pelo usuário.
        Se a pessoa quiser praticar o inglês dela, você deve pegar os níveis das pessoas para ter como base de conhecimento e respostas.
        Em momento algum ensine a pessoa a falar palavrões ou xingar, estamos tratando de conteúdos educativos.
        Responda de maneira objetiva.
        Quero que você leia a mensagem inteira que a pessoa mandou, interprete o texto e verifique se há algum erro gramatical, se houver, informe a pessoa e diga porque está errado, além de dar a solução correta.

        <context>
        {context}
        </context>
        """

        # Busca as informações sobre a questão do usuário. Faz um tipo de requisição (como se fosse uma query)
        docs = self.__retriever.invoke(question)

        # Forma um template para a IA, usando o langchain
        question_answering_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SYSTEM_TEMPLATE, # Passa a mensagem de sistema, que é o que foi definido anteriormente (prompt enviado para a IA)
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        document_chain = create_stuff_documents_chain(self.__chat, question_answering_prompt)

        response = document_chain.invoke(
            {
                "context": docs, # Troca a variável {context} do template pelos documentos que subiram no banco vetorizado
                "messages": self.__build_messages(history_messages, question), # Passa em messages o histórico de mensagens com o usuário
            }
        )

        # # Cria o chain a partir da pergunta, o modelo e a função da resposta do modelo para transformar em texto puro
        # chain = prompt | self.__chat | StrOutputParser()
    
        # # Processa a resposta
        # response = chain.invoke({
        #     "texto": question,
        # })

        return response