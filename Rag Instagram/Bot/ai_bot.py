import os
from decouple import config # Busca a variável de ambiente
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq # Busca os modelos do groq
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings

# Comunica com o groq
os.environ["GROQ_API_KEY"] = config("GROQ_API_KEY")

# Classe do bot
class AIBot():    
    # Inicializador
    def __init__(self):
        # Cria o modelo do Groq
        self.__chat = ChatGroq(model="llama-3.1-70b-versatile")
        # Cria um retriever, uma instância do banco de dadosd
        self.__retriever = self.__build_retriever()

    # Localiza o banco de dados e busca as informações conforme o prompt
    def __build_retriever(self):
        # Informa o local do banco de dados
        persist_directory = r"C:\Users\Nícolas Nasário\OneDrive\Cursos online\Treinamento Python - Hashtag\Códigos\Nexus Systems\Rag Instagram\Bot Data"
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
            # Verifica se a chave 'fromMe' está presente no dicionário
            message_class = HumanMessage if message.get("fromMe") else AIMessage
            messages.append(message_class(content=message.get("body", "")))

        # Adiciona a mensagem atual (pergunta)
        messages.append(HumanMessage(content=question))

        return messages

    # Recebe a mensagem do usuário e processa a partir de um prompt
    def invoke(self, question):
        SYSTEM_TEMPLATE = """
        Você é um assistente virtual especializado em criar conteúdos para publicações no Instagram de uma empresa chamada Nexus Systems. A empresa é especializada em automatizar processos, utilizando chatbots e outras tecnologias de programação. Sua tarefa é interpretar os textos enviados e gerar posts criativos e engajadores, focados em mostrar como a Nexus Systems pode transformar processos empresariais e otimizar fluxos de trabalho.

        Leve em consideração o histórico de projetos de automação realizados pela empresa, incluindo a criação de soluções personalizadas como chatbots, integrações de sistemas e automações complexas. O objetivo é destacar a inovação, eficiência e impacto dessas soluções nas empresas dos clientes.

        Quando o conteúdo envolver detalhes de projetos, forneça resumos ou destaques que mostrem o sucesso das automações implementadas, utilizando linguagem clara e acessível para um público que busca inovação e melhoria em seus processos.

        Seu trabalho é gerar posts que:

            Apresentem os principais benefícios da automação.
            Mostrem os resultados das implementações anteriores.
            Incentivem o engajamento com perguntas ou chamadas à ação.
            Ofereçam visões sobre como a Nexus Systems pode ajudar empresas a crescer e se adaptar ao futuro digital.

        Use emojis de forma criativa para tornar o conteúdo mais dinâmico e atraente. Lembre-se de que a Nexus Systems é uma empresa moderna e inovadora, e os posts devem refletir essa imagem.

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
                "messages": self.__build_messages(question=question, history_messages=None), # Passa em messages o histórico de mensagens com o usuário
            }
        )

        return response