import time
import redis

from settings import test_settings

if __name__ == '__main__':
    redis_client = redis.Redis(host=test_settings.redis_host, port=6379, db=0)
    while True:
        if redis_client.ping():
            break
        time.sleep(1)
