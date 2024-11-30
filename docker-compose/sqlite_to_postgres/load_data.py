import os
import sqlite3
from contextlib import closing
from typing import Generator, Optional
from datetime import datetime
from dateutil import parser
import psycopg
from dataclasses import astuple
from dotenv import load_dotenv
from psycopg.rows import dict_row
from datamodels import Genre, FilmWork, GenreFilmWork, Person, PersonFilmWork

load_dotenv()

dsl = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
}

BATCH_SIZE = 100

def get_table_sql(sqlite_cursor: sqlite3.Cursor, table: str) -> str:
    sqlite_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,))
    result = sqlite_cursor.fetchone()
    if not result:
        raise ValueError(f"Таблица {table} не найдена в базе данных SQLite.")
    return result['sql']

def extract_data(sqlite_cursor: sqlite3.Cursor, table: str) -> Generator[list[sqlite3.Row], None, None]:
    sqlite_cursor.execute(f'SELECT * FROM {table}')
    while results := sqlite_cursor.fetchmany(BATCH_SIZE):
        yield results



def transform_data(sqlite_cursor: sqlite3.Cursor, table: str, model) -> Generator[list, None, None]:
    for batch in extract_data(sqlite_cursor, table):
        transformed_batch = []
        for record in batch:
            record_dict = dict(record)

            if 'created_at' not in record_dict or record_dict['created_at'] is None:
                record_dict['created_at'] = datetime.now().isoformat()

            if 'updated_at' not in record_dict or record_dict['updated_at'] is None:
                record_dict['updated_at'] = datetime.now().isoformat()

            if 'updated_at' in record_dict:
                record_dict['modified'] = record_dict['updated_at']
                del record_dict['updated_at']
            if 'created_at' in record_dict:
                record_dict['created'] = record_dict['created_at']
                del record_dict['created_at']

            if 'description' in record_dict and record_dict['description'] is None:
                record_dict['description'] = ''

            if table == 'film_work':
                record_dict['creation_date'] = parser.parse(record_dict['created']).date().isoformat()

            transformed_batch.append(model(**record_dict))

        yield transformed_batch

def load_data(sqlite_cursor: sqlite3.Cursor, pg_cursor: psycopg.Cursor, table: str, model):
    for batch in transform_data(sqlite_cursor, table, model):
        query = generate_insert_query(table, batch[0])
        batch_as_tuples = [astuple(record) for record in batch]
        pg_cursor.executemany(query, batch_as_tuples)

def generate_insert_query(table: str, record) -> str:
    fields = ', '.join(record.__annotations__.keys())
    placeholders = ', '.join(['%s'] * len(record.__annotations__))
    return f'INSERT INTO content.{table} ({fields}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING'

if __name__ == '__main__':
    with closing(sqlite3.connect(os.getenv('SQLITE_DB_NAME'))) as sqlite_conn, closing(psycopg.connect(**dsl)) as pg_conn:
        sqlite_conn.row_factory = sqlite3.Row
        with closing(sqlite_conn.cursor()) as sqlite_cur, closing(pg_conn.cursor(row_factory=dict_row)) as pg_cur:

            tables = {
                'genre': Genre,
                'film_work': FilmWork,
                'genre_film_work': GenreFilmWork,
                'person': Person,
                'person_film_work': PersonFilmWork,
            }
            for table, model in tables.items():
                try:
                    table_sql = get_table_sql(sqlite_cur, table)
                    print(f'Таблица {table} найдена. SQL: {table_sql}')
                except ValueError as e:
                    print(e)
                    continue

                load_data(sqlite_cur, pg_cur, table, model)

            pg_conn.commit()

    print('🎉 Данные успешно перенесены !!!')
