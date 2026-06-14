import os
import shutil
from decouple import config # Importa as variáveis de ambiente
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config import RAG_FILES_DIR, VECTOR_STORE_PATH, HUGGINGFACE_API_KEY

os.environ["HUGGINGFACE_API_KEY"] = HUGGINGFACE_API_KEY

def load_documents():
    try:
        print(f"Processando documentos")
        docs = []
        processed_dir = os.path.join(RAG_FILES_DIR, "processed")
        os.makedirs(processed_dir, exist_ok=True)

        # if not os.path.exists(processed_dir):
        #     os.mkdir(processed_dir) # Cria uma pasta para os arquivos processados dentro de rag_files_dir

        # Forma a lista de arquivos a serem processados
        files = [
            os.path.join(RAG_FILES_DIR, file)
            for file in os.listdir(RAG_FILES_DIR) 
            if file.endswith('.pdf') or file.endswith('.txt') or file.endswith('.docx')
        ]

        print(f"Arquivos analisados: {files}")

        for file in files:
            print(f"Processando o arquivo: {file}")
            # Carrega o arquivo de acordo com a extensão
            loader = PyPDFLoader(file) if file.endswith('.pdf') else (
                TextLoader(file) if file.endswith('.txt') else Docx2txtLoader(file)
            )
            docs.extend(loader.load()) # Adiciona os documentos carregados na lista de documentos
            dest_path = os.path.join(processed_dir, os.path.basename(file)) # Cria o caminho de destino para o arquivo processado, com o nome do arquivo
            shutil.move(file, dest_path) # Move o arquivo para a pasta de arquivos processados

            print(f"Arquivo processado: {file} -> {dest_path}")

        # print(f"Documentos: {docs}")

        return docs # Retorna a lista de documentos carregados
    
    except Exception as e:
        print(f"Erro - Vector Store: {e}")


# Faz a vetorização dos documentos
def get_vectorstore():
    print(f"Carregando documentos no get_vectorstore")
    docs = load_documents() # Carrega os documentos
        
    if docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, # Quantidade de tokens de tamanho
            chunk_overlap=200, # Quantidade de tokens de overlap para fazer a ligação das informações
        )

        splits = text_splitter.split_documents(
            documents=docs
        )

        print(f"Documentos carregados: {VECTOR_STORE_PATH}")

        chroma = Chroma(
            persist_directory=VECTOR_STORE_PATH,
            embedding_function=HuggingFaceEmbeddings(),
        )

        print(f"[HUGGINGFACE] Embedding function initialized.")

        chroma.add_documents(splits)
        
        return chroma
    
    print("Documentos carregados")
        
    return Chroma(
        embedding_function=HuggingFaceEmbeddings(), # Passa o modelo do banco
        persist_directory=VECTOR_STORE_PATH,
    )


if __name__ == "__main__":
    get_vectorstore()