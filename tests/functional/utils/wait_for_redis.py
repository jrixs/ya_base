import redis
import backoff


@backoff.on_exception(backoff.expo,
                      redis.RedisError,
                      max_tries=8,
                      max_time=60)
def wait_for_redis():
    redis_client = redis.Redis(host="test_redis",
                               port=6379, db=0)
    while True:
        if redis_client.ping():
            break


if __name__ == '__main__':
    wait_for_redis()
