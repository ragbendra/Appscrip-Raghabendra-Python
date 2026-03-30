import time
from app.config import settings

class SimpleTokenBucket:
    def __init__(self, capacity, refill_rate):
        # max tokens the bucket can hold
        self.capacity = capacity
        
        # tokens added per second
        self.refill_rate = refill_rate
        
        # store buckets per key (e.g., IP/user)
        self.buckets = {}

    def _get_bucket(self, key):
        # create bucket if not exists
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": self.capacity,
                "last_refill": time.time()
            }
        return self.buckets[key]

    def is_allowed(self, key):
        bucket = self._get_bucket(key)

        # calculate time passed
        now = time.time()
        elapsed = now - bucket["last_refill"]

        # refill tokens
        bucket["tokens"] += elapsed * self.refill_rate
        if bucket["tokens"] > self.capacity:
            bucket["tokens"] = self.capacity

        bucket["last_refill"] = now

        # check if request can be allowed
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, 0.0          # <-- Return 0 wait time if allowed
        else:
            deficit = 1 - bucket["tokens"]
            retry_after = deficit / self.refill_rate
            return False, round(retry_after, 2) # <-- Return wait time if denied

# Initialize it using your settings so other files can import it
token_bucket = SimpleTokenBucket(
    capacity=settings.TOKEN_BUCKET_CAPACITY, 
    refill_rate=settings.TOKEN_BUCKET_REFILL_RATE
)
