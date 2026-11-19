import numpy as np


def generate_workload(
    n_requests: int, arrival_rate: float, service_rate: float, seed: int | np.random.SeedSequence
) -> tuple[np.ndarray, np.ndarray]:
    if n_requests <= 0:
        raise ValueError("n_requests debe ser positivo")
    if arrival_rate <= 0 or service_rate <= 0:
        raise ValueError("Las tasas de llegada y de servicio deben ser positivas")
    rng = np.random.default_rng(seed)
    arrivals = np.add.accumulate(rng.exponential(1.0 / arrival_rate, n_requests))
    services = rng.exponential(1.0 / service_rate, n_requests)
    return arrivals, services


def spawn_seeds(seed: int, n: int) -> list[np.random.SeedSequence]:
    return np.random.SeedSequence(seed).spawn(n)
