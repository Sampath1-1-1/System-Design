# Extracted from manuscript/book1-traditional/09-real-time-communication.md §9.9.6 (listing 4). Edit the manuscript, not this file.
import random

def full_jitter_delay(attempt: int, base: float = 1.0, cap: float = 60.0) -> float:
    """'Full jitter': uniform in [0, min(cap, base * 2**attempt)] seconds."""
    return random.uniform(0, min(cap, base * (2 ** attempt)))

# illustrative client loop
# attempt = 0
# while not connected:
#     await asyncio.sleep(full_jitter_delay(attempt)); attempt += 1
#     connected = await try_connect()      # reset attempt = 0 after a stable minute
