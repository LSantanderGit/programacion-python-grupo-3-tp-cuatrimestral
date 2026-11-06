"""Escalon 0: baseline por eventos, ingenuo pero razonable."""

import numpy as np


class Request:
    """Un request: llegada, duracion del servicio y, tras simular, inicio y espera."""

    def __init__(self, index: int, arrival: float, service: float) -> None:
        self.index = index
        self.arrival = arrival
        self.service = service
        self.start = 0.0
        self.wait = 0.0


def simulate(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    """Simula una cola con ``servers`` workers y devuelve la espera en cola de cada request.

    Procesa un evento de llegada por request, en orden. Se crea un objeto ``Request`` por
    llegada y el worker se elige por busqueda lineal en una lista de instantes de
    liberacion: el que se libera primero (D1). Se hace ``inicio = max(llegada, libre)``
    y el worker queda libre en ``inicio + servicio``.

    Por que no es un hombre de paja: es el codigo que escribiria una persona sin buscar
    optimizar (objetos, listas, bucles), pero usa el algoritmo correcto por eventos, sin
    reloj discretizado (no agrega error de discretizacion) y con costo O(n*c), igual que
    los demas escalones. Las mejoras posteriores cambian la implementacion, no el modelo.
    """
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
