import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import shutil
from decouple import config  # Importa as variáveis de ambiente

# Busca as variáveis de ambiente
os.environ["GROQ_API_KEY"] = config("GROQ_API_KEY")
os.environ["HUGGINGFACE_API_KEY"] = config("HUGGINGFACE_API_KEY")

def safe_read_file(file_path):
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'utf-16']
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.read()
        except (UnicodeDecodeError, FileNotFoundError) as e:
            print(f"Erro ao ler o arquivo {file_path} com a codificação {encoding}: {str(e)}")
    return None

if __name__ == "__main__":
    # Define o caminho do diretório PDF para treinamento
    path = r"C:\Users\Nícolas Nasário\OneDrive\Cursos online\Treinamento Python - Hashtag\Códigos\Nexus Systems\Rag Instagram\Rag\Data"

    # Cria uma lista para armazenar os documentos carregados
    all_docs = []

    for file_path in os.listdir(path):        
        if file_path.endswith(".txt"):
            full_path = os.path.join(path, file_path)
            
            # Tenta ler o arquivo .txt com a função segura de leitura
            content = safe_read_file(full_path)
            if content:
                # Cria o loader a partir do conteúdo lido do arquivo
                loader = TextLoader(file_path=full_path, encoding="latin-1")
                
                # Adiciona o conteúdo do arquivo manualmente ao loader
                docs = loader.load()
                
                # Adiciona os documentos carregados à lista
                all_docs.extend(docs)

    # Splita a informação, dividindo em chunks e depois gera o overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Quantidade de tokens de tamanho
        chunk_overlap=200,  # Quantidade de tokens de overlap para fazer a ligação das informações
    )

    # Agora gera o split dos documentos
    chunks = text_splitter.split_documents(
        documents=all_docs,  # Passa a lista de documentos
    )

    # Pasta onde vai ficar o banco de dados
    persist_directory = r"C:\Users\Nícolas Nasário\OneDrive\Cursos online\Treinamento Python - Hashtag\Códigos\Nexus Systems\Rag Instagram\Bot Data"

    # Verifica se chroma_data já existe como diretório ou arquivo
    if os.path.exists(persist_directory):
        if os.path.isdir(persist_directory):
            shutil.rmtree(persist_directory)  # Remove o diretório e seu conteúdo
        else:
            os.remove(persist_directory)  # Se for um arquivo, remove o arquivo

    # Busca o modelo de embedding
    embedding = HuggingFaceEmbeddings()

    # Cria o banco de dados a partir das informações obtidas
    vector_store = Chroma(
        embedding_function=embedding,  # Passa o modelo do banco
        persist_directory=persist_directory,  # Informa o diretório onde o banco vai ser criado
    )

    # Gera os documentos no banco de dados
    vector_store.add_documents(
        documents=chunks,
    )