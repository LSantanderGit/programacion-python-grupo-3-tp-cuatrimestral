"""Escalon 2: Python idiomatico (sin objetos, variables locales, menos llamadas)."""

from heapq import heapreplace

import numpy as np


def simulate(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    """Misma simulacion, escrita para minimizar el overhead del interprete.

    - Sin objetos ``Request``: se itera directamente sobre listas de floats nativos
      (``tolist``), mas rapido que iterar sobre escalares de NumPy.
    - ``heapreplace`` hace pop + push en una sola llamada; ``heap[0]`` es el minimo.
    - Lista de salida preasignada y nombres locales (evita busquedas de atributos/globales).
    """
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
