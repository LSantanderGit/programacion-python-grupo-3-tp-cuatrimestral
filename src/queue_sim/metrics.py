"""Metricas comunes a todos los escalones (misma definicion de percentil para todos)."""

import numpy as np


def makespan(arrivals: np.ndarray, waits: np.ndarray, services: np.ndarray) -> float:
    """Instante en que termina el ultimo servicio."""
    return float(np.max(arrivals + waits + services))


def metrics(
    waits: np.ndarray,
    services: np.ndarray,
    servers: int,
    makespan: float | None = None,
    warmup_frac: float = 0.05,
) -> dict[str, float]:
    """Calcula metricas de una corrida.

    Se descarta el transitorio inicial (``warmup_frac`` de los primeros requests) para
    las medias y percentiles. Los percentiles usan ``np.percentile`` con el metodo por
    defecto (``linear``). El tiempo en el sistema (sojourn) es espera + servicio.
    La utilizacion usa todos los requests: ``sum(services) / (servers * makespan)``;
    si ``makespan`` es None se devuelve ``nan`` (ver ``makespan()``).
    """
    if not 0.0 <= warmup_frac < 1.0:
        raise ValueError("warmup_frac debe estar en [0, 1)")
    skip = int(len(waits) * warmup_frac)
    w = waits[skip:]
    sojourn = w + services[skip:]
    utilization = float(np.sum(services) / (servers * makespan)) if makespan else float("nan")
    return {
        "mean_wait": float(np.mean(w)),
        "mean_sojourn": float(np.mean(sojourn)),
        "p95_wait": float(np.percentile(w, 95)),
        "p95_sojourn": float(np.percentile(sojourn, 95)),
        "utilization": utilization,
    }
