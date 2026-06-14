from langchain_community.chat_message_histories import RedisChatMessageHistory
from config import REDIS_URL


def get_session_history(session_id):
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        # decode_responses=True, # Isso pode ser necessário se você quiser decodificação de strings no history, mas o RedisChatMessageHistory deve lidar com isso internamente
    )
    