from heapq import heapreplace

import numpy as np


def simulate(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    heap = [0.0] * servers
    waits = [0.0] * len(arrivals)
    for i, (arrival, service) in enumerate(zip(arrivals.tolist(), services.tolist())):
        free = heap[0]
        if free > arrival:
            waits[i] = free - arrival
            heapreplace(heap, free + service)
        else:
            heapreplace(heap, arrival + service)
    return np.array(waits)
