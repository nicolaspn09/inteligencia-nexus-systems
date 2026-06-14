# from flask import Flask, request

# app = Flask(__name__)

# @app.route('/webhook', methods=['POST'])
# def webhook():
#     data = request.json
#     print(data)
#     return "Webhook received", 200

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5002)


### ENVIA MENSAGEM
import requests
import json

url = "https://evolution2.nexussystemsai.shop/message/sendText/Suyanne"

payload = json.dumps({
  "number": "5548999044726",
  "text": "X-alface",  # Corrigido para usar "text" diretamente
  "options": {
    "delay": 1200,
    "presence": "composing",
    "linkPreview": False
  }
})
headers = {
  'Content-Type': 'application/json',
  'apikey': 'eWeisGuXMhYoxjYCR8umEjA82tPxx0NR'
}

response = requests.post(url, headers=headers, data=payload)

print(response.text)



### LER MENSAGENS
import requests
import json

url = "https://evolution2.nexussystemsai.shop/webhook/set/Suyanne"

payload = json.dumps({
  "webhook": {
    "url": "http://92.113.38.183:5002/webhook",  # URL do seu webhook
    "enabled": True,  # Habilita o webhook
    "webhook_by_events": True,  # Habilita para eventos
    "webhook_base64": False,
    "events": [
      "QRCODE_UPDATED",
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "MESSAGES_DELETE",
      "SEND_MESSAGE",
      "CONNECTION_UPDATE",
      "CALL"
    ]
  }
})

headers = {
  'Content-Type': 'application/json',
  'apikey': 'eWeisGuXMhYoxjYCR8umEjA82tPxx0NR'
}

response = requests.post(url, headers=headers, data=payload)

print(response.json())