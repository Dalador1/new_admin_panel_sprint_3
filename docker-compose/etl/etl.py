from typing import List, Dict, Any
from elasticsearch import Elasticsearch, helpers
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import psycopg2
import redis
import logging
import time
import backoff


class RedisState:
    def __init__(self, redis_host: str, redis_port: int):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

    def get_state(self, key: str) -> Any:
        return self.redis_client.get(key)

    def set_state(self, key: str, value: Any):
        self.redis_client.set(key, value)


class ElasticsearchLoader:
    def __init__(self, es_host: str, index_name: str):
        self.es = Elasticsearch([es_host])
        self.index_name = index_name

    def load_data(self, data: List[Dict[str, Any]]):
        if not data:
            logging.info("Нет данных для загрузки.")
            return

        actions = [
            {
                "_op_type": "index",
                "_index": self.index_name,
                "_id": record["id"],
                "_source": record,
            }
            for record in data
        ]

        helpers.bulk(self.es, actions)
        logging.info(f"Загружено {len(data)} записей в Elasticsearch.")


class PostgresReader:
    def __init__(self, dsn: str):
        self.dsn = dsn

    @staticmethod
    @backoff.on_exception(backoff.expo, psycopg2.OperationalError, max_time=60)
    def _connect_with_backoff(dsn):
        return psycopg2.connect(dsn)

    def fetch_data_since(self, table: str, last_id: str) -> List[Dict[str, Any]]:
        with self._connect_with_backoff(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"SELECT * FROM {table} WHERE id > %s ORDER BY id ASC;", (last_id,))
                return cursor.fetchall()


def transform_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    transformed = []
    for record in data:
        transformed.append({
            "id": record["id"],
            "title": record.get("title", ""),
            "description": record.get("description", ""),
            "imdb_rating": record.get("rating", 0),
            "genres": record.get("genres", "").split(",") if record.get("genres") else [],
            "actors": [{"id": actor_id, "name": name} for actor_id, name in zip(record.get("actors_ids", []), record.get("actors_names", []))],
            "directors": [{"id": director_id, "name": name} for director_id, name in zip(record.get("directors_ids", []), record.get("directors_names", []))],
            "writers": [{"id": writer_id, "name": name} for writer_id, name in zip(record.get("writers_ids", []), record.get("writers_names", []))],
        })
    return transformed


def run_etl():
    logging.basicConfig(level=logging.INFO)

    load_dotenv()
    postgres_dsn = (
        f"dbname={os.getenv('DB_NAME')} "
        f"user={os.getenv('DB_USER')} "
        f"password={os.getenv('DB_PASSWORD')} "
        f"host={os.getenv('DB_HOST')} "
        f"port={os.getenv('DB_PORT')}"
    )
    es_host = os.getenv("ELASTIC_HOST", "http://localhost:9200")
    redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    index_name = os.getenv("ELASTIC_INDEX", "movies")
    state_key = "last_processed_id"
    poll_interval = int(os.getenv("POLL_INTERVAL", 15))

    loader = ElasticsearchLoader(es_host, index_name)
    reader = PostgresReader(postgres_dsn)
    state = RedisState(redis_host, redis_port)

    while True:
        try:
            last_id = state.get_state(state_key) or "0"
            raw_data = reader.fetch_data_since("content.film_work", last_id)
            if not raw_data:
                logging.info("Нет новых данных для загрузки.")
            else:
                transformed_data = transform_data(raw_data)
                loader.load_data(transformed_data)
                new_last_id = raw_data[-1]["id"]
                state.set_state(state_key, new_last_id)
                logging.info(f"Состояние обновлено: последний обработанный ID = {new_last_id}")
        except Exception as e:
            logging.error(f"Ошибка во время ETL: {e}")
        logging.info(f"Ожидание {poll_interval} секунд перед следующим опросом...")
        time.sleep(poll_interval)


if __name__ == "__main__":
    run_etl()