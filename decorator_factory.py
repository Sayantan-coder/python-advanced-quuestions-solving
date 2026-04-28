import time
import functools


class RateLimitExceeded(Exception):
    pass


def rate_limit(calls_per_second, burst_limit):
    def decorator(func):
        tokens = burst_limit
        last_refill = time.time()

        @functools.wraps(func)
        def wrapper(*args, block=True, **kwargs):
            nonlocal tokens, last_refill

            while True:
                current_time = time.time()

                time_passed = current_time - last_refill
                new_tokens = time_passed * calls_per_second

                tokens = min(burst_limit, tokens + new_tokens)
                last_refill = current_time

                if tokens >= 1:
                    tokens -= 1
                    return func(*args, **kwargs)
                else:
                    if not block:
                        raise RateLimitExceeded("Too many requests!")

                    time.sleep(0.1)

        return wrapper

    return decorator


class APIClient:

    @rate_limit(calls_per_second=2, burst_limit=3)
    def fetch_data(self, i):
        print(f"Fetching data {i} at time {round(time.time(), 2)}")


client = APIClient()

for i in range(10):
    client.fetch_data(i)
