import requests
from config import (
    EVOLUTION_API_URL, 
    EVOLUTION_INSTANCE_NAME,
    EVOLUTION_API_KEY,
)

def send_whatsapp_message(number, text):
    # Monta a base de URL para enviar a mensagem
    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE_NAME}"

    # Monta o cabeçalho da requisição
    # O cabeçalho é onde estão os dados que identificam a requisição
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json",
    }

    # Monta o payload da requisição
    # O payload é o corpo da requisição, onde estão os dados que queremos enviar
    payload = {
        "number": number,
        "text": text,
    }

    print(f"[EVOLUTION_API] Enviando para URL: {url}")
    print(f"[EVOLUTION_API] Headers: {headers}")
    print(f"[EVOLUTION_API] Payload: {payload}")

    # Faz a requisição POST para enviar a mensagem
    # A requisição POST é usada para enviar dados para o servidor
    # requests.post(url=url, headers=headers, json=payload)

    try:
        response = requests.post(url=url, headers=headers, json=payload)
        response.raise_for_status() # Levanta um erro para status de erro (4xx ou 5xx)
        print(f"[EVOLUTION_API] Resposta da API: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[EVOLUTION_API] Erro ao enviar mensagem: {e}")


if __name__ == "__main__":
    send_whatsapp_message("5548999044726", "Olá")