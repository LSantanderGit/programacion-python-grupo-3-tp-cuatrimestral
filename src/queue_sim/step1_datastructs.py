"""Escalon 1: estructuras de datos adecuadas (deque, heapq, __slots__)."""

import heapq
from collections import deque

import numpy as np


class Request:
    """Request con ``__slots__``: menos memoria y acceso a atributos mas rapido."""

    __slots__ = ("arrival", "service")

    def __init__(self, arrival: float, service: float) -> None:
        self.arrival = arrival
        self.service = service


def simulate(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    """Misma simulacion que el baseline, con estructuras mejores.

    - ``deque`` de llegadas pendientes (``popleft`` es O(1)).
    - ``heapq`` con los instantes de liberacion de los workers: el que se libera primero
      sale en O(log c) en lugar de la busqueda lineal O(c).
    - ``__slots__`` en ``Request``.
    """
    pending = deque(Request(float(a), float(s)) for a, s in zip(arrivals, services))
    free_at = [0.0] * servers  # una lista de ceros ya es un heap valido
    waits = []
    while pending:
        req = pending.popleft()
        earliest = heapq.heappop(free_at)
        start = max(req.arrival, earliest)
        waits.append(start - req.arrival)
        heapq.heappush(free_at, start + req.service)
    return np.array(waits)
