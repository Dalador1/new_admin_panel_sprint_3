import redis
from logger import setup_logger

logger = setup_logger("RedisState")


class RedisState:
    def __init__(self, host: str, port: int, db: int = 0):
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)

    def get_state(self, key: str) -> str:
        state = self.redis_client.get(key)
        logger.info(f"Получено состояние для ключа {key}: {state}")
        return state

    def set_state(self, key: str, value: str):
        self.redis_client.set(key, value)
        logger.info(f"Обновлено состояние для ключа {key}: {value}")