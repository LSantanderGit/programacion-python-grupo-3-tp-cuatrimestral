"""Escalon 4: Numba (@njit(cache=True), array de tiempos libres con argmin)."""

import time

import numpy as np
from numba import njit


@njit(cache=True)
def _simulate_numba(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    n = len(arrivals)
    waits = np.empty(n, dtype=np.float64)
    free_at = np.zeros(servers, dtype=np.float64)

    for i in range(n):
        arr = arrivals[i]
        srv = services[i]
        worker = np.argmin(free_at)
        earliest = free_at[worker]
        if earliest > arr:
            waits[i] = earliest - arr
            free_at[worker] = earliest + srv
        else:
            waits[i] = 0.0
            free_at[worker] = arr + srv

    return waits


def simulate(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    """Simula una cola con ``servers`` workers usando Numba JIT.

    Implementa el contrato D3: simulate(arrivals, services, servers) -> waits.
    Utiliza un array de tiempos libres y selecciona en cada iteracion el worker
    que se libera primero con ``np.argmin`` (D1).
    """
    arr = np.asarray(arrivals, dtype=np.float64)
    srv = np.asarray(services, dtype=np.float64)
    return _simulate_numba(arr, srv, int(servers))


def warmup() -> float:
    """Ejecuta una corrida minima para forzar la compilacion JIT y devuelve el tiempo transcurrido."""
    dummy_arr = np.array([0.0, 1.0], dtype=np.float64)
    dummy_srv = np.array([1.0, 1.0], dtype=np.float64)
    t0 = time.perf_counter()
    _simulate_numba(dummy_arr, dummy_srv, 1)
    _simulate_numba(dummy_arr, dummy_srv, 2)
    return time.perf_counter() - t0
