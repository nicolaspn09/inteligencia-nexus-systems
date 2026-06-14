import os
import build
import psycopg2
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def diretorio_json():
    return r"token.json"


# Função que obtém a margem informada pelo usuário
def solicita_tabela_sheets(id_planilha, range_dados):
    """
    Solicita as informações do Google Sheet, guia de margens

    Returns:
    Valores: collection
    """
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"] #Acessa o google sheets

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = id_planilha
    SAMPLE_RANGE_NAME = range_dados

    creds = None

    # Faz o login da API do Google
    if os.path.exists(diretorio_json()):
        creds = Credentials.from_authorized_user_file(diretorio_json(), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(diretorio_json(), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(diretorio_json(), 'w') as token:
            token.write(creds.to_json())

    # Faz a leitura e edição da planilha
    #try:
    service = build('sheets', 'v4', credentials=creds)

    # Ler informacoes do Google Sheets
    sheet = service.spreadsheets()
    # Lê a planilha através do .get, o .update altera informações
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    valores = result['values']

    # Retorna uma lista
    return valores


tabela = solicita_tabela_sheets("1tE5Vz0oeoyRISIlMI1HAebLWefViI69NTzJu3pDJBEI", "A2:C")
print(tabela)


# PEGAR OS DADOS DO SHEETS, PREENCHER NO BANCO DE DADOS (NEXUS), VERIFICAR SE O ALUNO NÃO EXISTE MAIS NA PLANILHA, SE NÃO EXISTIR, EXCLUIR DO BANCO DE DADOS (NEXUS)

# PEGAR OS DADOS DO BANCO DE DADOS E USAR PARA O CHATBOT, SE O ALUNO NÃO EXISTIR NO BANCO DE DADOS, DAR UM RETORNO DE QUE NÃO É ALUNO.

# BANCO: CHATBOT.SUYYOURWAY

# CRIAR CONEXÃO VIA GOOGLE SHEETS API