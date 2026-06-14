import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Se você modificar esses escopos, exclua o arquivo token.json.
# 'https://www.googleapis.com/auth/calendar.events' já inclui permissão para ler e escrever eventos.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Caminhos dos arquivos de credenciais e token (ajuste para o seu ambiente)
TOKEN_PATH = r'C:\Users\nicol\OneDrive\Cursos online\Treinamento Python - Hashtag\Códigos\Nexus Systems\Chatbot - Taciano\Chatbot\calendar\token.json'
CREDENTIALS_PATH = r'C:\Users\nicol\OneDrive\Cursos online\Treinamento Python - Hashtag\Códigos\Nexus Systems\Chatbot - Taciano\Chatbot\calendar\credentials.json'

def get_google_calendar_service():
    """Autentica e retorna o objeto de serviço da API do Google Calendar."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def check_availability(service, start_time_iso, end_time_iso, calendar_id='primary'):
    """
    Verifica a disponibilidade para um slot de tempo específico.
    Retorna True se estiver livre, False caso contrário.
    """
    print(f"Verificando disponibilidade de {start_time_iso} a {end_time_iso} no calendário '{calendar_id}'...")
    body = {
        "timeMin": start_time_iso,
        "timeMax": end_time_iso,
        "items": [{"id": calendar_id}]
    }
    try:
        free_busy_result = service.freebusy().query(body=body).execute()
        # A resposta de free/busy contém um dicionário 'calendars'
        # e, dentro dele, o ID do seu calendário.
        # 'busy' será uma lista de slots ocupados.
        busy_slots = free_busy_result['calendars'][calendar_id]['busy']

        if not busy_slots:
            print("Horário DISPONÍVEL.")
            return True
        else:
            print("Horário OCUPADO.")
            return False
    except HttpError as error:
        print(f'Ocorreu um erro ao verificar disponibilidade: {error}')
        return False

def create_calendar_event(service, summary, start_time_iso, end_time_iso,
                          description='', location='', calendar_id='primary',
                          time_zone='America/Sao_Paulo'):
    """
    Cria um evento na agenda.
    """
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time_iso,
            'timeZone': time_zone,
        },
        'end': {
            'dateTime': end_time_iso,
            'timeZone': time_zone,
        },
    }
    print(f"Tentando criar evento: '{summary}' em {start_time_iso}")
    try:
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print('Evento criado com sucesso: %s' % (event.get('htmlLink')))
        return True
    except HttpError as error:
        print('Ocorreu um erro ao criar o evento: %s' % error)
        return False

def main():
    service = get_google_calendar_service()

    # --- Simulação da entrada do usuário ---
    # Em um chatbot real, esses valores viriam da interpretação da mensagem do usuário.
    # Exemplo: O usuário diz "Tem horário livre dia 18 de Junho às 14h?"
    dia_str = "18"
    mes_str = "06"
    ano_str = "2025" # Lembre-se que estamos em 2025-06-14
    hora_inicio_str = "14:00"
    duracao_minutos = 60 # Duração padrão do treino

    try:
        # Constrói o objeto datetime a partir da entrada do usuário
        ano = int(ano_str)
        mes = int(mes_str)
        dia = int(dia_str)
        hora_inicio_partes = [int(p) for p in hora_inicio_str.split(':')]
        hora = hora_inicio_partes[0]
        minuto = hora_inicio_partes[1]

        # Define o fuso horário (ajuste conforme a sua localização)
        fuso_horario = datetime.timezone(datetime.timedelta(hours=-3)) # Exemplo: UTC-3 (São Paulo)
        
        # Constrói o objeto datetime com o fuso horário
        start_datetime = datetime.datetime(ano, mes, dia, hora, minuto, tzinfo=fuso_horario)
        end_datetime = start_datetime + datetime.timedelta(minutes=duracao_minutos)

        # Converte para o formato ISO 8601 exigido pela API
        start_time_iso = start_datetime.isoformat()
        end_time_iso = end_datetime.isoformat()

        # 1. Verificar disponibilidade
        if check_availability(service, start_time_iso, end_time_iso):
            print("\nHorário disponível! Prosseguindo para agendamento...")
            # 2. Se estiver livre, agendar
            summary = "Treino de Boxe - Agendamento via Chatbot"
            description = f"Agendado para o dia {dia_str}/{mes_str} às {hora_inicio_str}."
            location = "Arena Marcial" # Pode ser um valor fixo ou obtido de outro lugar

            if create_calendar_event(service, summary, start_time_iso, end_time_iso,
                                     description=description, location=location):
                print("Agendamento concluído com sucesso!")
            else:
                print("Falha ao agendar o horário.")
        else:
            print("\nHorário indisponível. Por favor, escolha outro horário.")

    except ValueError:
        print("Formato de data ou hora inválido. Por favor, forneça o dia, mês, ano e hora (ex: 18 06 2025 14:00).")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == '__main__':
    main()