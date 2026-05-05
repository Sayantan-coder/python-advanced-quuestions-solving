import asyncio
from async_decorator import async_timeout, AsyncTimeoutError


@async_timeout(2)
async def fast_task():
    await asyncio.sleep(1)
    return "completed"


async def main():
    result = await fast_task()
    print("Test 1 result:", result)


asyncio.run(main())


@async_timeout(5)
async def long_task():
    try:
        print("Task started")
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("Inner task cancelled!")
        raise


async def main():
    task = asyncio.create_task(long_task())

    await asyncio.sleep(1)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("Outer task cancelled")


asyncio.run(main())
