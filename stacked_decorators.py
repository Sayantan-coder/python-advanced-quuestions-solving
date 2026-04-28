import time
import functools


EXECUTION_LOG = []


def validate_input(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        annotations = func.__annotations__

        for arg, value in zip(annotations.keys(), args):
            expected_type = annotations[arg]
            if not isinstance(value, expected_type):
                raise TypeError(f"{arg} must be {expected_type}")

        return func(*args, **kwargs)

    return wrapper


def log_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()

        log = {
            "function": func.__name__,
            "args": args,
            "kwargs": kwargs,
            "result": result,
            "time_taken": round(end_time - start_time, 4),
            "from_cache": False,
        }

        EXECUTION_LOG.append(log)

        return result

    return wrapper


def cache_result(ttl_seconds):
    def decorator(func):
        cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(kwargs.items()))

            current_time = time.time()

            if key in cache:
                result, timestamp = cache[key]

                if current_time - timestamp < ttl_seconds:
                    return result  # return cached result (NO logging)

            result = func(*args, **kwargs)

            cache[key] = (result, current_time)

            return result

        return wrapper

    return decorator


@validate_input
@cache_result(ttl_seconds=5)
@log_execution
def add(a: int, b: int) -> int:
    time.sleep(1)
    return a + b


print(add(2, 3))
print(add(2, 3))
print(add(4, 5))

print("\nExecution Log:")
for log in EXECUTION_LOG:
    print(log)
