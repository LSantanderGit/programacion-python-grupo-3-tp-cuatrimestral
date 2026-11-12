"""Escalon 5: Paralelismo (replicas Monte Carlo con ProcessPoolExecutor)."""

from concurrent.futures import ProcessPoolExecutor
from typing import Any

import numpy as np

from queue_sim.metrics import metrics
from queue_sim.step4_numba import simulate as step4_simulate
from queue_sim.workload import generate_workload


def simulate(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    """Implementa el contrato comun simulate(arrivals, services, servers) -> waits.

    Para una unica corrida secuencial, delega en el kernel optimizado de Numba (escalon 4).
    """
    return step4_simulate(arrivals, services, servers)


def _worker_simulate(
    args: tuple[int, float, float, int, np.random.SeedSequence | int, bool],
) -> Any:
    """Worker top-level para ProcessPoolExecutor (compatible con Windows 'spawn')."""
    n_requests, arrival_rate, service_rate, servers, seed, return_metrics = args
    arrivals, services = generate_workload(n_requests, arrival_rate, service_rate, seed)
    waits = step4_simulate(arrivals, services, servers)
    if return_metrics:
        return metrics(waits, services, servers)
    return waits


def simulate_replicas(
    n_requests: int,
    arrival_rate: float,
    service_rate: float,
    servers: int,
    seeds: list[np.random.SeedSequence] | list[int],
    max_workers: int | None = None,
    return_metrics: bool = False,
) -> list[Any]:
    """Ejecuta R replicas Monte Carlo en paralelo con ProcessPoolExecutor.

    Cada replica genera su propia carga de trabajo usando su semilla hija (D7).
    Si ``return_metrics=True``, calcula las metricas en el worker y devuelve solo
    el diccionario de metricas, evitando serializar grandes arrays por IPC.
    """
    tasks = [
        (n_requests, arrival_rate, service_rate, servers, s, return_metrics)
        for s in seeds
    ]
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(_worker_simulate, tasks))


def simulate_replicas_serial(
    n_requests: int,
    arrival_rate: float,
    service_rate: float,
    servers: int,
    seeds: list[np.random.SeedSequence] | list[int],
    return_metrics: bool = False,
) -> list[Any]:
    """Ejecuta R replicas Monte Carlo en serie con el escalon 4 (base de comparacion D7)."""
    tasks = [
        (n_requests, arrival_rate, service_rate, servers, s, return_metrics)
        for s in seeds
    ]
    return [_worker_simulate(t) for t in tasks]
