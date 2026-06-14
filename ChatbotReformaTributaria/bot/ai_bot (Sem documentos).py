import os
from decouple import config # Busca a variável de ambiente
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq # Busca os modelos do groq

# Comunica com o groq
os.environ["GROQ_API_KEY"] = config("GROQ_API_KEY")

# Classe do bot
class AIBot():    
    # Inicializador
    def __init__(self):
        # Cria o modelo do Groq
        self.__chat = ChatGroq(model="llama-3.1-70b-versatile")

    # Recebe a mensagem do usuário e processa a partir de um prompt
    def invoke(self, question):
        prompt = PromptTemplate(
            input_variables=["texto"],
            # Monta um template de prompts

            # MODELO?: Você é um atendente de um grupo do whats referente ao jogo de futebol que acontece aos sábados
            template= """
            Você é um assistente virtual, interprete o texto enviado pelo usuário e ache a melhor resposta
            <texto>
            {texto}
            </texto>
            """
        )

        # Cria o chain a partir da pergunta, o modelo e a função da resposta do modelo para transformar em texto puro
        chain = prompt | self.__chat | StrOutputParser()
    
        # Processa a resposta
        response = chain.invoke({
            "texto": question,
        })

        return response