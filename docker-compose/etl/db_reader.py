from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import backoff
from logger import setup_logger

logger = setup_logger("PostgresReader")


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
                data = cursor.fetchall()
        logger.info(f"Извлечено {len(data)} записей из таблицы {table}.")
        return data