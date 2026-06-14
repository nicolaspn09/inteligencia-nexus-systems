from fastapi import FastAPI, Request
from message_buffer import buffer_message
from evolution_api import send_whatsapp_message
from analisator_chain import get_message_introduction


app = FastAPI()


# Subindo o endpoint para o webhook
# Foi criada uma rota para o webhook
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json() # Pega o json do request
    print(data)

    # Pega o número do telefone
    chat_id = data.get("data").get("key").get("remoteJid")

    # Pega a mensagem enviada
    message = data.get("data").get("message").get("conversation")

    ######## PARA PEGAR O PRIMEIRO CONTATO, ENVIAR À LLM INTERPRETAR, ELE VAI NOS RETORNAR APENAS SIM OU NÃO.
    ######## DEPOIS, SE NÃO FOR UM CONTATO INICIAL, VAMOS PEGAR O QUE O CLIENTE ESTÁ INFORMANDO, PASSAR PARA A LLM E POSTAR AS MENSAGENS DE ACORDO COM O QUE A IA RESPONDER. SE FOR ALGO SOBRE AS DÚVIDAS, AÍ SIM VAMOS ENVIAR AO BUFFER, SENÃO, VAMOS ACESSAR CADA MÓDULO DE MANEIRA SEPARADA.

    # Verifica se o chat_id e a mensagem não estão vazios e se não é um grupo
    if chat_id and message and "@g.us" not in chat_id:
        print(f"Mensagem recebida de {chat_id}: {message}")

        # Aqui você pode chamar a LLM para analisar a mensagem e verificar se é um contato inicial
        response = get_message_introduction(message)
        print(f"Resposta da LLM: {response.content}")

        if "sim" in str(response).lower():
            # Alunos ou demais pessoas que não são alunos
            if "91150894" not in chat_id:
                send_whatsapp_message(
                    number=chat_id,
                    text=f"Olá, bem vindo ao MarcialBot! Você pode escolher as seguintes opções (digite apenas o número):\n\n"
                    "1 - Agendar horário de treino!\n"
                    "2 - Alterar horário de treino!\n"
                    "3 - Cancelar horário de treino!\n"
                    "4 - Quero ser aluno!\n"
                    "5 - Sobre a Arena Marcial!\n"
                    "6 - Dúvidas sobre os treinos!\n"
                    "7 - Sair!"
                )
            
            else:
                send_whatsapp_message(
                    number=chat_id,
                    text=f"Olá Kuririn, bem vindo ao MarcialBot! Você pode escolher as seguintes opções:\n\n"
                    "1 - Alterar horário de treino!\n"
                    "2 - Consultar horário de treino!\n"
                    "3 - Cancelar horário de treino!\n"
                    "4 - Sair!"
                )

        elif "sair" not in str(response).lower():
            await buffer_message(
                chat_id=chat_id,
                message=message,
            )

        print(f"Mensagem enviada para {chat_id}: {message}")
    
    return {"status": "ok"}