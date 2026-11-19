import heapq
from collections import deque

import numpy as np


class Request:
    __slots__ = ("arrival", "service")

    def __init__(self, arrival: float, service: float) -> None:
        self.arrival = arrival
        self.service = service


def simulate(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    pending = deque(Request(float(a), float(s)) for a, s in zip(arrivals, services))
    free_at = [0.0] * servers
    waits = []
    while pending:
        req = pending.popleft()
        earliest = heapq.heappop(free_at)
        start = max(req.arrival, earliest)
        waits.append(start - req.arrival)
        heapq.heappush(free_at, start + req.service)
    return np.array(waits)
