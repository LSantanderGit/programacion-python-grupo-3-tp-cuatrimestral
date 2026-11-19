import numpy as np


def makespan(arrivals: np.ndarray, waits: np.ndarray, services: np.ndarray) -> float:
    return float(np.max(arrivals + waits + services))


def metrics(
    waits: np.ndarray,
    services: np.ndarray,
    servers: int,
    makespan: float | None = None,
    warmup_frac: float = 0.05,
) -> dict[str, float]:
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
