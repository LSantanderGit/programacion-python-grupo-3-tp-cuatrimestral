"""Configuracion de la matriz de tamanos y perfiles de benchmarks (D6)."""

from dataclasses import dataclass, field

import psutil


@dataclass(frozen=True)
class BenchmarkProfile:
    """Configuracion de parametros para un perfil de ejecucion de benchmarks."""

    name: str
    reps: int
    sizes_slow: list[int]
    sizes_fast: list[int]
    servers_list: list[int]
    parallel_n: int
    parallel_servers: int
    parallel_reps: int
    parallel_workers: list[int] = field(default_factory=list)


def get_profile(mode: str = "quick") -> BenchmarkProfile:
    """Devuelve el perfil de configuracion para el modo especificado ('quick' o 'full')."""
    logical_cores = psutil.cpu_count(logical=True) or 4
    worker_candidates = [1, 2, 4, 8, logical_cores, 16]
    workers = sorted(set(worker_candidates))

    if mode == "quick":
        return BenchmarkProfile(
            name="quick",
            reps=3,
            sizes_slow=[1_000, 10_000, 50_000],
            sizes_fast=[1_000, 10_000, 50_000, 100_000],
            servers_list=[1, 2],
            parallel_n=50_000,
            parallel_servers=2,
            parallel_reps=8,
            parallel_workers=[w for w in workers if w <= max(8, logical_cores)],
        )
    elif mode == "full":
        return BenchmarkProfile(
            name="full",
            reps=7,
            sizes_slow=[1_000, 10_000, 100_000, 500_000, 1_000_000],
            sizes_fast=[1_000, 10_000, 100_000, 1_000_000, 5_000_000, 10_000_000],
            servers_list=[1, 2, 4, 8],
            parallel_n=1_000_000,
            parallel_servers=8,
            parallel_reps=24,
            parallel_workers=workers,
        )
    else:
        raise ValueError(f"Modo desconocido: '{mode}'. Opciones validas: 'quick', 'full'.")


# Constantes comunes del experimento
RHO_DEFAULT = 0.75
SERVICE_RATE_DEFAULT = 1.0
BASE_SEED = 2026
