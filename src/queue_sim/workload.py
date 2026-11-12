"""Generacion de la carga de trabajo (unica fuente de aleatoriedad del proyecto)."""

import numpy as np


def generate_workload(
    n_requests: int, arrival_rate: float, service_rate: float, seed: int | np.random.SeedSequence
) -> tuple[np.ndarray, np.ndarray]:
    """Genera llegadas y servicios exponenciales.

    Devuelve ``(arrivals, services)``: ``arrivals`` son tiempos absolutos de llegada
    (suma acumulada de interarribos exponenciales de tasa ``arrival_rate``) y
    ``services`` son duraciones exponenciales de tasa ``service_rate``.
    """
    if n_requests <= 0:
        raise ValueError("n_requests debe ser positivo")
    if arrival_rate <= 0 or service_rate <= 0:
        raise ValueError("Las tasas de llegada y de servicio deben ser positivas")
    rng = np.random.default_rng(seed)
    arrivals = np.add.accumulate(rng.exponential(1.0 / arrival_rate, n_requests))
    services = rng.exponential(1.0 / service_rate, n_requests)
    return arrivals, services


def spawn_seeds(seed: int, n: int) -> list[np.random.SeedSequence]:
    """Devuelve ``n`` semillas hijas independientes a partir de ``seed`` (una por replica)."""
    return np.random.SeedSequence(seed).spawn(n)
