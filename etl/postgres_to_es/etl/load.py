import os

import backoff
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout
from etl.connect import log

load_dotenv()

es_host = os.environ.get('ES_HOST', 'http://127.0.0.1:9200')


def process_bulk_response(response) -> bool:
    if response['errors']:
        for item in response['items']:
            if 'error' in item['index']:
                log.error(f"Ошибка индексации: {item['index']['error']}")
        return False
    else:
        log.debug("Все данные успешно записаны или обновлены в Elasticsearch")
        return True


@backoff.on_exception(backoff.expo,
                      (ConnectionError, ConnectionTimeout),
                      max_tries=5)
def bulk_load(data):
    es = Elasticsearch(es_host)
    respons = es.bulk(body=data)
    return process_bulk_response(respons)
