import time
from concurrent.futures import Executor, ProcessPoolExecutor
from typing import Any

import numpy as np

from queue_sim.metrics import metrics
from queue_sim.step4_numba import simulate as step4_simulate
from queue_sim.workload import generate_workload


def simulate(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    return step4_simulate(arrivals, services, servers)


def _worker_simulate(
    args: tuple[int, float, float, int, np.random.SeedSequence | int, bool],
) -> Any:
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
    tasks = [
        (n_requests, arrival_rate, service_rate, servers, s, return_metrics)
        for s in seeds
    ]
    return [_worker_simulate(t) for t in tasks]


def _warm_task(_: int) -> int:
    step4_simulate(np.array([0.0, 1.0]), np.array([1.0, 1.0]), 2)
    time.sleep(0.3)
    return 0


def warm_pool(executor: ProcessPoolExecutor, workers: int) -> None:
    list(executor.map(_warm_task, range(workers)))


def simulate_replicas_in_pool(
    executor: Executor,
    n_requests: int,
    arrival_rate: float,
    service_rate: float,
    servers: int,
    seeds: list[np.random.SeedSequence] | list[int],
    return_metrics: bool = False,
) -> list[Any]:
    tasks = [
        (n_requests, arrival_rate, service_rate, servers, s, return_metrics)
        for s in seeds
    ]
    return list(executor.map(_worker_simulate, tasks))
