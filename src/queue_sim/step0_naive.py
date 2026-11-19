import numpy as np


class Request:
    def __init__(self, index: int, arrival: float, service: float) -> None:
        self.index = index
        self.arrival = arrival
        self.service = service
        self.start = 0.0
        self.wait = 0.0


def simulate(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    requests = [
        Request(i, float(a), float(s)) for i, (a, s) in enumerate(zip(arrivals, services))
    ]
    free_at = [0.0] * servers
    for req in requests:
        worker = 0
        for j in range(1, servers):
            if free_at[j] < free_at[worker]:
                worker = j
        req.start = max(req.arrival, free_at[worker])
        req.wait = req.start - req.arrival
        free_at[worker] = req.start + req.service
    return np.array([req.wait for req in requests])
