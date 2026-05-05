import time
import functools
from collections import OrderedDict, namedtuple

CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "current_size", "evictions"])


def _freeze(obj):

    if isinstance(obj, list):

        return tuple(_freeze(item) for item in obj)

    elif isinstance(obj, dict):

        return tuple(sorted((_freeze(k), _freeze(v)) for k, v in obj.items()))

    elif isinstance(obj, set):

        return frozenset(_freeze(item) for item in obj)

    else:

        return obj


def _make_key(args, kwargs, include_self=True):

    effective_args = args if include_self else args[1:]

    frozen_args = tuple(_freeze(a) for a in effective_args)

    frozen_kwargs = tuple(sorted((_freeze(k), _freeze(v)) for k, v in kwargs.items()))

    return (frozen_args, frozen_kwargs)


def smart_cache(maxsize=128, ttl=None, include_self=True):

    def decorator(func):

        cache = OrderedDict()

        hits = [0]
        misses = [0]
        evictions = [0]

        def _is_expired(entry):

            if ttl is None:
                return False
            age = time.monotonic() - entry["timestamp"]
            return age > ttl

        def _evict_expired():

            expired_keys = [k for k, v in cache.items() if _is_expired(v)]
            for k in expired_keys:
                del cache[k]
                evictions[0] += 1

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            key = _make_key(args, kwargs, include_self=include_self)

            if key in cache:
                entry = cache[key]

                if not _is_expired(entry):
                    hits[0] += 1
                    entry["access_count"] += 1

                    cache.move_to_end(key)
                    return entry["result"]
                else:

                    del cache[key]
                    evictions[0] += 1

            misses[0] += 1

            if len(cache) >= maxsize:

                _evict_expired()

                if len(cache) >= maxsize:
                    cache.popitem(last=False)
                    evictions[0] += 1

            result = func(*args, **kwargs)
            cache[key] = {
                "result": result,
                "timestamp": time.monotonic(),
                "access_count": 1,
            }

            cache.move_to_end(key)

            return result

        def cache_info():

            return CacheInfo(
                hits=hits[0],
                misses=misses[0],
                current_size=len(cache),
                evictions=evictions[0],
            )

        def cache_clear():

            cache.clear()
            hits[0] = 0
            misses[0] = 0
            evictions[0] = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear

        return wrapper

    return decorator


if __name__ == "__main__":

    @smart_cache(maxsize=3, ttl=10)
    def add(a, b):
        print(f"  [computing] add({a}, {b})")
        return a + b

    print(add(1, 2))
    print(add(3, 4))
    print(add(5, 6))
    print(add(7, 8))
    print(add(1, 2))
    print(add.cache_info())
    add.cache_clear()
    print("After clear:", add.cache_info())

    @smart_cache(maxsize=5)
    def process(data, config):
        print(f"  [computing] process({data}, {config})")
        return sum(data)

    print(process([1, 2, 3], {"mode": "sum"}))
    print(process([1, 2, 3], {"mode": "sum"}))
    print(process([4, 5, 6], {"mode": "sum"}))
    print(process.cache_info())

    @smart_cache(maxsize=5, ttl=0.5)
    def slow_query(x):
        print(f"  [computing] slow_query({x})")
        return x * 10

    print(slow_query(7))
    print(slow_query(7))
    time.sleep(0.6)
    print(slow_query(7))
    print(slow_query.cache_info())

    class Calculator:

        def __init__(self, name):
            self.name = name

        @smart_cache(maxsize=10, include_self=True)
        def square(self, n):
            print(f"  [{self.name}] computing square({n})")
            return n * n

    c1 = Calculator("C1")
    c2 = Calculator("C2")
    print(c1.square(4))
    print(c1.square(4))
    print(c2.square(4))
    print(c1.square.cache_info())
