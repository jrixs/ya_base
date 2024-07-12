from elasticsearch import Elasticsearch, ConnectionError
import backoff


@backoff.on_exception(backoff.expo, 
                      ConnectionError,
                      max_tries=8,
                      max_time=60)
def wait_for_es():
    es_client = Elasticsearch(hosts="http://test_elasticsearch:9200")
    while True:
        if es_client.ping():
            break


if __name__ == '__main__':
    wait_for_es()
