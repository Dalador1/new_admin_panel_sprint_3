from typing import List, Dict, Any
from elasticsearch import Elasticsearch, helpers
import backoff
from logger import setup_logger

logger = setup_logger("ElasticsearchLoader")


class ElasticsearchLoader:
    def __init__(self, es_host: str, index_name: str):
        self.es = Elasticsearch([es_host])
        self.index_name = index_name

    @backoff.on_exception(backoff.expo, Exception, max_time=60)
    def load_data(self, data: List[Dict[str, Any]]):
        if not data:
            logger.info("Нет данных для загрузки.")
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

        try:
            helpers.bulk(self.es, actions)
            logger.info(f"Успешно загружено {len(data)} записей в Elasticsearch.")
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных в Elasticsearch: {e}")
            raise