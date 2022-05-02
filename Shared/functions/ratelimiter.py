import asyncio
import dataclasses
import time


@dataclasses.dataclass
class RateLimiter:
    """
    Gives out x tokens for network operations every y seconds
    """

    max_tokens: int = 240  # how many requests can we save up - bungie limits after 250 in 10s, so will put that to 240
    seconds: int = 10  # in how many seconds those requests are allowed

    tokens: float = dataclasses.field(init=False)
    updated_at: float = dataclasses.field(init=False)

    lock: asyncio.Lock = dataclasses.field(init=False, default=asyncio.Lock())

    def __post_init__(self):
        self.tokens = self.max_tokens

    async def wait_for_token(self):
        """Waits until a token becomes available"""

        async with self.lock:
            if self.tokens == 0:
                current_time = time.time()
                if (missing := current_time - self.updated_at) < self.seconds:
                    await asyncio.sleep(self.seconds - missing)
                self.tokens = self.max_tokens

            if self.tokens == self.max_tokens:
                # the first request is made, start the timer when that should fill back up
                self.updated_at = time.time()

            self.tokens -= 1
