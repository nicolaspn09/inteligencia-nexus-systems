import logging
import requests
import time
import random
import json
import datetime
from flask import Flask, request, jsonify
from bot.ai_bot import AIBot


app = Flask(__name__)

# Configurando o logging para capturar todos os logs
logging.basicConfig(level=logging.DEBUG)

# Dicionário global para armazenar o histórico das mensagens
message_history = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    # Inicializa o bot
    bot = AIBot()
    
    app.logger.debug("Entrando no webhook")  # Usando logger ao invés de print
    data = request.get_json()  # Recebe o JSON enviado pelo webhook
    
    if data:
        # Exibe os dados para verificar se o webhook está sendo recebido corretamente
        app.logger.debug(f"Dados recebidos do Webhook: {data}")
        
        # Processa os dados conforme necessário
        event = data.get("event")
        if event == "messages.upsert":
            # Extrair o número de telefone (sem o domínio)
            remote_jid = data.get("data", {}).get("key", {}).get("remoteJid", "")
            number = remote_jid.split('@')[0]  # Pega apenas o número (sem o @whatsapp.net)
            
            # Extrair a mensagem
            conversation = data.get("data", {}).get("message", {}).get("conversation", "Sem mensagem")

            # Extrair quem é a pessoa
            from_me = data.get("data", {}).get("key", {}).get("fromMe", "")

            # Extraindo o senderTimestamp
            sender_timestamp_str = data.get("data", {}).get("message", {}).get("messageContextInfo", {}).get("deviceListMetadata", {}).get("senderTimestamp", "")

            sender_timestamp = int(sender_timestamp_str)

            # Converte o timestamp para datetime em UTC
            dt_utc = datetime.datetime.fromtimestamp(sender_timestamp, tz=datetime.timezone.utc)
            # print(f"Timestamp convertido para UTC: {dt_utc}")

            # Obtém a hora atual em UTC-3 (ajustando automaticamente para o fuso horário São Paulo)
            # now_utc_minus_3 = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
            now_utc_minus_3 = datetime.datetime.now(datetime.timezone.utc)
            # print(f"Hora atual em UTC-3: {now_utc_minus_3}")

            # Calcula a diferença de tempo entre agora (UTC-3) e o timestamp ajustado
            time_difference = now_utc_minus_3 - dt_utc
            # print(f"Diferença de tempo entre a mensagem e o momento atual: {time_difference}")

            # Verifica se a diferença é menor que 1 hora
            # if time_difference < datetime.timedelta(hours=1):            
            app.logger.debug(f"Mensagem recebida: {conversation}")
            app.logger.debug(f"Remetente: {number}")
            app.logger.debug(f"From me: {from_me}")
            app.logger.debug(f"Tempo da mensagem: {time_difference}")
                
            # Gravar a mensagem no histórico
            update_message_history(number, conversation)

            # Recupera o histórico das últimas 5 mensagens
            history_messages = message_history.get(number, [])

            if from_me == False:
                # Busca a resposta da IA
                response = bot.invoke(history_messages=history_messages, question=conversation)
                
                # Enviar mensagem de volta
                send_message(number, response)
        
    else:
        app.logger.debug("Nenhum dado JSON recebido ou o formato está incorreto.")
    
    return jsonify({'status': 'success'}), 201


def update_message_history(number, message):
    """
    Atualiza o histórico de mensagens para o número fornecido. 
    Mantém as últimas 5 mensagens.
    """
    if number not in message_history:
        message_history[number] = []

    # Adiciona a nova mensagem
    message_history[number].append(message)

    # Mantém apenas as últimas x mensagens
    if len(message_history[number]) > 3:
        message_history[number] = message_history[number][-3:]

    app.logger.debug(f"Histórico de mensagens para {number}: {message_history[number]}")


def send_message(number, message):
    url = "https://rpa-evolution-api.2hswyv.easypanel.host/message/sendText/Nexus"
    
    # Formata o payload com o número e a mensagem
    payload = json.dumps({
        "number": number,
        "text": f"{message}",  # Envia a mensagem recebida de volta
        "options": {
            "delay": time.sleep(random.randint(1, 5)),
            "presence": "composing",
            "linkPreview": False
        }
    })
    
    headers = {
        'Content-Type': 'application/json',
        'apikey': '429683C4C977415CAAFCCE10F7D57E11'
    }
    
    # Envia a requisição
    response = requests.post(url, headers=headers, data=payload)
    
    app.logger.debug(f"Resposta da API: {response.text}")


@app.route('/get_history/<number>', methods=['GET'])
def get_history(number):
    """
    Rota para retornar o histórico de mensagens de um número.
    Retorna as últimas 5 mensagens trocadas com o número.
    """
    if number in message_history:
        history = message_history[number]
        return jsonify({"status": "success", "history": history}), 200
    else:
        return jsonify({"status": "error", "message": "Histórico não encontrado."}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)