import time
import redis


if __name__ == '__main__':
    redis_client = redis.Redis(host="test_redis",
                               port=6379, db=0)
    while True:
        if redis_client.ping():
            break
        time.sleep(1)
