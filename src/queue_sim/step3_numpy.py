import numpy as np

from queue_sim.step2_idiomatic import simulate as simulate_loop


def _lindley(arrivals: np.ndarray, services: np.ndarray) -> np.ndarray:
    increments = services[:-1] - np.diff(arrivals)
    z = np.concatenate(([0.0], np.add.accumulate(increments)))
    return z - np.minimum.accumulate(z)


def simulate(arrivals: np.ndarray, services: np.ndarray, servers: int) -> np.ndarray:
    if servers == 1:
        return _lindley(arrivals, services)
    return simulate_loop(arrivals, services, servers)
