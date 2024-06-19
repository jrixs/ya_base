import logging
import os
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler

import backoff
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor

load_dotenv()


def get_logger():
    logs_dir = os.environ.get('ES_LOGS', './')

    logger = logging.getLogger('ETL_Logger')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    handler = RotatingFileHandler(f'{logs_dir}etl_log.log',
                                  maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


log = get_logger()


@contextmanager
def pg_connect(dsl):
    conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    try:
        yield conn
    finally:
        conn.close()


@backoff.on_exception(backoff.expo,
                      psycopg2.OperationalError,
                      max_tries=5)
def tryfetchmany(pg_conn, sqlreq: str, lines=50):
    pg_conn.execute(sqlreq)
    while data := pg_conn.fetchmany(lines):
        yield data
