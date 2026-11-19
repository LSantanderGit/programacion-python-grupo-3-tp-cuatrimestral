import sys
import time

import numpy as np

from queue_sim import step1_datastructs, step4_numba
from queue_sim.workload import generate_workload


def run_smoke_benchmark(n: int = 20_000, servers: int = 2, min_ratio: float = 5.0) -> bool:
    print(f"=== Ejecutando Smoke Benchmark (n={n:,}, servers={servers}, min_ratio={min_ratio}x) ===")

    step4_numba.warmup()

    arrivals, services = generate_workload(n, 0.75 * servers, 1.0, seed=42)

    t1_list = []
    for _ in range(3):
        t0 = time.perf_counter()
        step1_datastructs.simulate(arrivals, services, servers)
        t1_list.append(time.perf_counter() - t0)
    t1_med = float(np.median(t1_list))

    t4_list = []
    for _ in range(3):
        t0 = time.perf_counter()
        step4_numba.simulate(arrivals, services, servers)
        t4_list.append(time.perf_counter() - t0)
    t4_med = float(np.median(t4_list))

    ratio = t1_med / t4_med if t4_med > 0 else 0.0
    print(f"-> Escalon 1 (Estructuras): {t1_med * 1000:6.2f} ms")
    print(f"-> Escalon 4 (Numba JIT):   {t4_med * 1000:6.2f} ms")
    print(f"-> Ratio de aceleracion (Step1 / Step4): {ratio:.2f}x (Umbral requerido: {min_ratio:.2f}x)")

    if ratio < min_ratio:
        print(f"[ERROR] Regresion detectada: el ratio {ratio:.2f}x es menor al umbral {min_ratio:.2f}x", file=sys.stderr)
        return False

    print("[OK] Smoke benchmark aprobado exitosamente.")
    return True


if __name__ == "__main__":
    success = run_smoke_benchmark()
    sys.exit(0 if success else 1)
