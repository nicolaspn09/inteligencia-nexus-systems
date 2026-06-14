import asyncio
import redis.asyncio as redis
from collections import defaultdict
from config import REDIS_URL, BUFFER_KEY_SUFIX, DEBOUNCE_SECONDS, BUFFER_TTL
from evolution_api import send_whatsapp_message
from chains import get_conversational_rag_chain


redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
print(f"Usuário redis: {redis_client}")
conversational_rag_chain = get_conversational_rag_chain()
debounce_tasks = dict()

def log(*args):
    print("[BUFFER]", *args)


async def buffer_message(chat_id, message):
    buffer_key = f"{chat_id}{BUFFER_KEY_SUFIX}"
    log(f"Buffer key: {buffer_key}")

    await redis_client.rpush(buffer_key, message) #Salva no redis a chave única do número e a mensagem do usuário
    await redis_client.expire(buffer_key, BUFFER_TTL) #Tempo de expiração

    log(f"Mensagem adicionada ao buffer de: {chat_id} - {message}")

    # Cancela a task anterior se existir e ainda estiver em execução
    if chat_id in debounce_tasks:
        task = debounce_tasks[chat_id]
        if not task.done():
            task.cancel()
            log(f"Debounce resetado para {chat_id}")
        else:
            log(f'Debounce para {chat_id} já concluído ou falhou antes do reset. Re-criando.')

    log(f"Iniciando debounce tasks")

    debounce_tasks[chat_id] = asyncio.create_task(handle_debounce(chat_id=chat_id)) #Cria uma task para o debounce, que vai esperar o tempo de debounce para enviar a mensagem agrupada

    log(f"Task criada para {chat_id}")


async def handle_debounce(chat_id):
    log(f"Entrou em handle_debounce para {chat_id}")

    try:
        log(f"Iniciando debounce para {chat_id}")

        await asyncio.sleep(float(DEBOUNCE_SECONDS))

        buffer_key = f"{chat_id}{BUFFER_KEY_SUFIX}"

        log(f"Buffer Key: {buffer_key}")

        messages = await redis_client.lrange(buffer_key, 0, -1) #Assim que passar o delay, vai fazer uma busca de mensagens com o ID do whats, funciona tipo um select no banco do redis

        log(f"Messages: {buffer_key}")

        full_messages = " ".join(messages).strip() #Reune tudo em uma só mensagem

        log(f"Full message: {full_messages}")

        if full_messages:
            log(f"Enviando mensagem agrupada à IA, do {chat_id}")

            try:
                ai_response = conversational_rag_chain.invoke(
                    input={"input": full_messages},
                    config={"configurable": {"session_id": chat_id}},
                )["answer"]
                log(f"DEBUG: IA respondeu para {chat_id}")
                
            except Exception as e_ai:
                if "internal server error" in str(e_ai).lower():
                    try:
                        log(f"Erro de servidor interno, aguardando {DEBOUNCE_SECONDS} segundos para tentar novamente.")

                        await asyncio.sleep(float(DEBOUNCE_SECONDS))

                        ai_response = conversational_rag_chain.invoke(
                            input={"input": full_messages},
                            config={"configurable": {"session_id": chat_id}},
                        )["answer"]
                        log(f"DEBUG: IA respondeu para {chat_id}")

                    except Exception as e_ai:
                        log(f"ERRO IA: {e_ai} para {chat_id}")
                        ai_response = f"Desculpe, não consegui gerar uma resposta no momento. Erro: {e_ai}"

            if "</think>" in ai_response:
                ai_response = ai_response.split("</think>")[1]

            send_whatsapp_message(
                number=chat_id,
                text=ai_response,            
            )

            log(f"Mensagem enviada para o {chat_id}: {ai_response}")

        await redis_client.delete(buffer_key) #Limpa o buffer

    except Exception as e:
        log(f"Erro: {e}")

    except asyncio.CancelledError:
        log(f"Debounce cancelado para {chat_id}")

    finally:
        log(f"Debounce finalizado para {chat_id}")