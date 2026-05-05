import time, random, asyncio, functools
from collections import deque
from enum import Enum
from typing import Tuple, Type


class CircuitOpenError(Exception):
    pass


class CircuitState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(
        self, faliure_threshold: int, recovery_timeout: float, max_history: int = 100
    ):
        self.state = CircuitState.CLOSED
        self.failure_threshold = faliure_threshold
        self.recovery_timeout = recovery_timeout
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.failure_history: deque = deque(maxlen=max_history)

    def allow_call(self):
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            else:
                return False
        if self.state == CircuitState.HALF_OPEN:
            return True
        return False

    def record_failure(self, exc: Exception):
        now = time.time()
        self.failure_history.append((now, exc))
        self.consecutive_failures += 1
        self.last_failure_time = now
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            return
        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def record_success(self):
        self.consecutive_failures = 0
        self.state = CircuitState.CLOSED

    def reset(self):
        self.consecutive_failures = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self.failure_history.clear()


def _get_wait_time(strategy: str, attempt: int, base_delay: float) -> float:

    if strategy == "fixed":

        return base_delay

    elif strategy == "exponential":

        return base_delay * (2**attempt)

    elif strategy == "jitter":

        exp_backoff = base_delay * (2**attempt)
        return random.uniform(0, exp_backoff)

    else:
        raise ValueError(
            f"Unknown backoff strategy: '{strategy}'. Use 'fixed', 'exponential', or 'jitter'."
        )


def retry(
    max_attempts: int = 3,
    exceptions: Tuple[Type[Exception]] = (Exception,),
    backoff_strategy: str = "fixed",
    base_delay: float = 1.0,
    failure_threshold: int = 3,
    recovery_timeout: float = 30.0,
    max_history: int = 100,
):

    def decorator(func):

        circuit = CircuitBreaker(failure_threshold, recovery_timeout, max_history)

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):

                for attempt in range(max_attempts):

                    if not circuit.allow_call():

                        raise CircuitOpenError(
                            f"Circuit breaker is OPEN for '{func.__name__}'. "
                            f"Consecutive failures: {circuit.consecutive_failures}. "
                            f"Try again after {circuit.recovery_timeout}s."
                        )

                    try:

                        result = await func(*args, **kwargs)

                        circuit.record_success()
                        return result

                    except exceptions as exc:

                        circuit.record_failure(exc)

                        is_last_attempt = attempt == max_attempts - 1
                        if is_last_attempt:

                            raise

                        wait = _get_wait_time(backoff_strategy, attempt, base_delay)
                        await asyncio.sleep(wait)

            async_wrapper.reset = circuit.reset

            async_wrapper.circuit = circuit
            return async_wrapper

        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):

                for attempt in range(max_attempts):

                    if not circuit.allow_call():
                        raise CircuitOpenError(
                            f"Circuit breaker is OPEN for '{func.__name__}'. "
                            f"Consecutive failures: {circuit.consecutive_failures}. "
                            f"Try again after {circuit.recovery_timeout}s."
                        )

                    try:

                        result = func(*args, **kwargs)

                        circuit.record_success()
                        return result

                    except exceptions as exc:

                        circuit.record_failure(exc)

                        is_last_attempt = attempt == max_attempts - 1
                        if is_last_attempt:
                            raise

                        wait = _get_wait_time(backoff_strategy, attempt, base_delay)
                        time.sleep(wait)

            sync_wrapper.reset = circuit.reset
            sync_wrapper.circuit = circuit
            return sync_wrapper

    return decorator


if __name__ == "__main__":

    call_count = 0

    @retry(
        max_attempts=2,
        exceptions=(ValueError,),
        backoff_strategy="fixed",
        base_delay=0.1,
        failure_threshold=3,
        recovery_timeout=2.0,
    )
    def unstable_service(should_fail: bool):
        global call_count
        call_count += 1
        if should_fail:
            raise ValueError(f"Service failed! (call #{call_count})")
        return f"Success on call #{call_count}"

    for i in range(3):
        try:
            unstable_service(should_fail=True)
        except (ValueError, CircuitOpenError) as e:
            print(f"  Caught [{type(e).__name__}]: {e}")

    print(f"\n  Circuit state: {unstable_service.circuit.state}")
    try:
        unstable_service(should_fail=True)
    except CircuitOpenError as e:
        print(f"  CircuitOpenError caught! ✓")

    unstable_service.reset()
    print(f"  After reset: {unstable_service.circuit.state}")
    print(f"  Failure history length: {len(unstable_service.circuit.failure_history)}")

    async def run_async_test():
        attempt_count = 0

        @retry(
            max_attempts=3,
            exceptions=(ConnectionError,),
            backoff_strategy="exponential",
            base_delay=0.05,
            failure_threshold=5,
            recovery_timeout=5.0,
        )
        async def async_api_call(succeed_on_attempt: int):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < succeed_on_attempt:
                raise ConnectionError(f"Network error on attempt {attempt_count}")
            return f"Async success on attempt {attempt_count}"

        result = await async_api_call(succeed_on_attempt=3)
        print(f"  Result: {result}")
        print(f"  Circuit state: {async_api_call.circuit.state}")

    asyncio.run(run_async_test())

    for i in range(4):
        wait = _get_wait_time("jitter", attempt=i, base_delay=1.0)
        print(f"  Attempt {i}: wait = {wait:.4f}s  (max possible = {1.0 * 2**i:.2f}s)")

    @retry(
        max_attempts=1, exceptions=(RuntimeError,), failure_threshold=10, max_history=3
    )
    def always_fails():
        raise RuntimeError("I always fail")

    for _ in range(5):
        try:
            always_fails()
        except RuntimeError:
            pass

    history = always_fails.circuit.failure_history
    print(f"  Failures attempted: 5 | History stored: {len(history)} (maxlen=3) ")
    for ts, exc in history:
        print(f"    {time.strftime('%H:%M:%S', time.localtime(ts))} — {exc}")
