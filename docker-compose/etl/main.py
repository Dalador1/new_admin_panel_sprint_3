from config import Settings
from db_reader import PostgresReader
from es_loader import ElasticsearchLoader
from redis_state import RedisState
from transformer import transform_data
from logger import setup_logger
import time

logger = setup_logger("ETL")


def run_etl():
    reader = PostgresReader(Settings.postgres_dsn)
    loader = ElasticsearchLoader(Settings.es_host, Settings.es_index)
    state = RedisState(Settings.redis_host, Settings.redis_port, Settings.redis_db)

    state_key = "last_processed_id"

    while True:
        try:
            last_id = state.get_state(state_key) or "0"
            raw_data = reader.fetch_data_since("content.film_work", last_id)
            if not raw_data:
                logger.info("Нет новых данных для обработки.")
            else:
                transformed_data = transform_data(raw_data)
                loader.load_data(transformed_data)
                new_last_id = raw_data[-1]["id"]
                state.set_state(state_key, new_last_id)
                logger.info(f"Состояние обновлено: последний обработанный ID = {new_last_id}")
        except Exception as e:
            logger.error(f"Ошибка во время ETL: {e}")
        logger.info(f"Ожидание {Settings.poll_interval} секунд перед следующим опросом...")
        time.sleep(Settings.poll_interval)


if __name__ == "__main__":
    run_etl()