"""Escalon 3: NumPy (vectorizacion en bloque).

Para c=1 la recurrencia de Lindley ``W[i+1] = max(0, W[i] + S[i] - T[i])`` (con ``T[i]``
el interarribo entre i e i+1) se resuelve sin bucle. Sea ``Z[0] = 0`` y ``Z[k] = sum_{i<k}
(S[i] - T[i])``. Entonces ``W[k] = Z[k] - min_{j<=k} Z[j]``, que son un ``add.accumulate`` y un
``minimum.accumulate``.

Para c>1 NO funciona: el estado es un vector de c instantes de liberacion y cada paso
elige y reemplaza el minimo (``argmin``). Esa dependencia no es una suma/maximo de
escalares acumulables, asi que no hay scan vectorizable; se usa el bucle con heap
(escalon 2 reutilizado).
"""

import numpy as np

from queue_sim.step2_idiomatic import simulate as simulate_loop


def _lindley(arrivals: np.ndarray, services: np.ndarray) -> np.ndarray:
    increments = services[:-1] - np.diff(arrivals)
    z = np.concatenate(([0.0], np.add.accumulate(increments)))
    return z - np.minimum.accumulate(z)


def simulate(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    """Simula la cola. c=1: vectorizado (Lindley); c>1: bucle con heap."""
    if servers == 1:
        return _lindley(arrivals, services)
    return simulate_loop(arrivals, services, servers)
