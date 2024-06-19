import os
from time import sleep

from dotenv import load_dotenv
from etl.connect import pg_connect, log
from etl.extract import сheck_filmwork, сheck_genre, сheck_person
import backoff
from psycopg2 import OperationalError

load_dotenv()


@backoff.on_exception(backoff.expo, OperationalError, max_tries=5,
                      on_backoff=lambda details: log.warning(
                        'Подключение не удалось, попытка номер: %s',
                        details['tries']),
                      on_giveup=lambda details: log.error(
                        'Превышено максимальное количество подключения: %s',
                        details['tries']))
def start(dsl):
    with pg_connect(dsl) as conn:
        set_uuid = сheck_filmwork(conn)
        set_uuid = сheck_person(conn, set_uuid)
        сheck_genre(conn, set_uuid)


if __name__ == '__main__':
    dsl = {
        'dbname': os.environ.get('DB_NAME', 'movies_database'),
        'user': os.environ.get('DB_USER', 'app'),
        'password': os.environ.get('DB_PASSWORD', '123qwe'),
        'host': os.environ.get('DB_HOST', '127.0.0.1'),
        'port': int(os.environ.get('DB_PORT', '5432'))
    }

    while True:
        start(dsl)
        sleep(60)
