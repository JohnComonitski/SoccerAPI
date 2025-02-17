import time

class RateLimiter:
    def __init__(self, max_calls, interval):
        self.max_calls = max_calls
        self.interval = interval
        self.calls = 0
        self.last_reset = time.time()

    def call(self, func, url):
        current_time = time.time()
        elapsed_time = current_time - self.last_reset

        if elapsed_time >= self.interval:
            self.calls = 0
            self.last_reset = current_time

        if self.calls >= self.max_calls:
            time.sleep(self.interval - elapsed_time)
            self.calls = 0
            self.last_reset = time.time()

        self.calls += 1
        return func(url)

