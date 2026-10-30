# Extracted from manuscript/book1-traditional/06-operating-systems.md §6.15.5 (listing 8). Edit the manuscript, not this file.
"""10,000 concurrent 'requests', one thread, about one second."""
import asyncio
import time


async def handle_request(i: int) -> int:
    await asyncio.sleep(1.0)        # stands in for a 1 s network call; yields to the loop
    return i


async def main() -> None:
    start = time.perf_counter()
    results = await asyncio.gather(*(handle_request(i) for i in range(10_000)))
    elapsed = time.perf_counter() - start
    print(f"{len(results)} requests finished in {elapsed:.2f} s on one thread")


asyncio.run(main())
