from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple


class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.clients: Dict[str, Tuple[int, datetime]] = defaultdict(lambda: (0, datetime.min))
    
    async def is_allowed(self, client_id: str) -> bool:
        now = datetime.now()
        count, last_reset = self.clients[client_id]
        
        if now - last_reset > timedelta(seconds=self.time_window):
            self.clients[client_id] = (1, now)
            return True
        
        if count < self.max_requests:
            self.clients[client_id] = (count + 1, last_reset)
            return True
        
        return False