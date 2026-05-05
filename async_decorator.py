import asyncio
import time
from functools import wraps


class AsyncTimeoutError(Exception):
    def __init__(self, func_name, elapsed, partial_result=None):
        self.func_name = func_name
        self.elapsed = elapsed
        self.partial_result = partial_result

        message = (
            f"Function '{func_name}' timed out after {elapsed:.2f}s. "
            f"Partial result: {partial_result}"
        )
        super().__init__(message)


def async_timeout(seconds, on_timeout=None, retry_on_timeout=0):

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            loop = asyncio.get_event_loop()
            if not loop.is_running():
                raise RuntimeError(
                    f"{func.__name__} must be called inside an async event loop"
                )

            last_exception = None

            for attempt in range(retry_on_timeout + 1):

                start_time = time.time()
                partial_result = None

                task = asyncio.create_task(func(*args, **kwargs))

                try:
                    result = await asyncio.wait_for(task, timeout=seconds)
                    return result

                except asyncio.TimeoutError:
                    elapsed = time.time() - start_time

                    task.cancel()

                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                    error = AsyncTimeoutError(func.__name__, elapsed, partial_result)

                    last_exception = error

                    if on_timeout:
                        await on_timeout(error)

                    if attempt == retry_on_timeout:
                        raise error

                except asyncio.CancelledError:

                    task.cancel()
                    raise

                except Exception as e:
                    task.cancel()
                    raise e

            raise last_exception

        return wrapper

    return decorator
