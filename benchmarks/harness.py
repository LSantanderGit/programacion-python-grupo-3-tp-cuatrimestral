import csv
import json
import random
import time
import tracemalloc
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
from radon.complexity import cc_visit
from radon.raw import analyze

from benchmarks.config import (
    BASE_SEED,
    RHO_DEFAULT,
    SERVICE_RATE_DEFAULT,
    BenchmarkProfile,
    get_profile,
)
from benchmarks.env_info import save_env_info
from queue_sim import (
    step0_naive,
    step1_datastructs,
    step2_idiomatic,
    step3_numpy,
    step4_numba,
    step5_parallel,
)
from queue_sim.workload import generate_workload, spawn_seeds

STEPS = [
    ("step0_naive", step0_naive.simulate, False),
    ("step1_datastructs", step1_datastructs.simulate, False),
    ("step2_idiomatic", step2_idiomatic.simulate, False),
    ("step3_numpy", step3_numpy.simulate, True),
    ("step4_numba", step4_numba.simulate, True),
]

DEPENDENCIES_MAP = {
    "step0_naive": [],
    "step1_datastructs": [],
    "step2_idiomatic": [],
    "step3_numpy": ["numpy"],
    "step4_numba": ["numba"],
    "step5_parallel": [],
}


def compute_code_metrics(src_dir: str = "src/queue_sim") -> list[dict[str, Any]]:
    metrics_list = []
    base_path = Path(src_dir)
    step_files = [
        ("step0_naive", "step0_naive.py"),
        ("step1_datastructs", "step1_datastructs.py"),
        ("step2_idiomatic", "step2_idiomatic.py"),
        ("step3_numpy", "step3_numpy.py"),
        ("step4_numba", "step4_numba.py"),
        ("step5_parallel", "step5_parallel.py"),
    ]

    for step_name, filename in step_files:
        filepath = base_path / filename
        if not filepath.exists():
            continue
        code = filepath.read_text(encoding="utf-8")
        raw = analyze(code)
        cc_blocks = cc_visit(code)
        cc_values = [b.complexity for b in cc_blocks] if cc_blocks else [1]
        avg_cc = round(sum(cc_values) / len(cc_values), 2)
        max_cc = max(cc_values)

        metrics_list.append(
            {
                "step": step_name,
                "file": filename,
                "loc": raw.loc,
                "sloc": raw.sloc,
                "comments": raw.comments,
                "avg_complexity": avg_cc,
                "max_complexity": max_cc,
                "new_dependencies": DEPENDENCIES_MAP.get(step_name, []),
            }
        )
    return metrics_list


def measure_times(profile: BenchmarkProfile) -> list[dict[str, Any]]:
    step4_numba.warmup()
    records = []

    all_sizes = sorted(set(profile.sizes_slow + profile.sizes_fast))

    for servers in profile.servers_list:
        arrival_rate = RHO_DEFAULT * servers * SERVICE_RATE_DEFAULT

        for n in all_sizes:
            active_steps = []
            for name, func, is_fast in STEPS:
                if is_fast and n in profile.sizes_fast or (not is_fast) and n in profile.sizes_slow:
                    active_steps.append((name, func))

            if not active_steps:
                continue

            arrivals, services = generate_workload(
                n, arrival_rate, SERVICE_RATE_DEFAULT, seed=BASE_SEED
            )

            times_by_step = {name: [] for name, _ in active_steps}

            for rep in range(profile.reps):
                order = list(active_steps)
                random.shuffle(order)
                for name, func in order:
                    t0 = time.perf_counter()
                    func(arrivals, services, servers)
                    dt = time.perf_counter() - t0
                    times_by_step[name].append(dt)

            for name, _ in active_steps:
                durations = times_by_step[name]
                q75, q25 = np.percentile(durations, [75, 25])
                records.append(
                    {
                        "step": name,
                        "n": n,
                        "servers": servers,
                        "median_s": float(np.median(durations)),
                        "iqr_s": float(q75 - q25),
                        "min_s": float(np.min(durations)),
                        "max_s": float(np.max(durations)),
                        "reps": profile.reps,
                    }
                )
    return records


def measure_memory(profile: BenchmarkProfile) -> list[dict[str, Any]]:
    step4_numba.warmup()
    records = []

    test_sizes = [s for s in [1_000, 10_000, 50_000] if s in profile.sizes_slow]
    servers = 2
    arrival_rate = RHO_DEFAULT * servers * SERVICE_RATE_DEFAULT

    for n in test_sizes:
        arrivals, services = generate_workload(
            n, arrival_rate, SERVICE_RATE_DEFAULT, seed=BASE_SEED
        )
        for name, func, _ in STEPS:
            tracemalloc.start()
            func(arrivals, services, servers)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            records.append(
                {
                    "step": name,
                    "n": n,
                    "servers": servers,
                    "peak_memory_kb": round(peak / 1024, 2),
                }
            )
    return records


def measure_parallel_scaling(profile: BenchmarkProfile) -> list[dict[str, Any]]:
    records = []
    n = profile.parallel_n
    servers = profile.parallel_servers
    r_reps = profile.parallel_reps
    arrival_rate = RHO_DEFAULT * servers * SERVICE_RATE_DEFAULT
    seeds = spawn_seeds(BASE_SEED, r_reps)

    t0 = time.perf_counter()
    step5_parallel.simulate_replicas_serial(
        n, arrival_rate, SERVICE_RATE_DEFAULT, servers, seeds, return_metrics=True
    )
    t_serial = time.perf_counter() - t0

    records.append(
        {
            "workers": 0,
            "mode": "serial_step4",
            "n": n,
            "servers": servers,
            "replicas": r_reps,
            "time_s": t_serial,
            "speedup": 1.0,
            "efficiency_pct": 100.0,
        }
    )

    for p in profile.parallel_workers:
        t0 = time.perf_counter()
        step5_parallel.simulate_replicas(
            n,
            arrival_rate,
            SERVICE_RATE_DEFAULT,
            servers,
            seeds,
            max_workers=p,
            return_metrics=True,
        )
        t_par = time.perf_counter() - t0
        sp = t_serial / t_par if t_par > 0 else 0.0
        eff = (sp / p) * 100.0 if p > 0 else 0.0

        records.append(
            {
                "workers": p,
                "mode": "parallel",
                "n": n,
                "servers": servers,
                "replicas": r_reps,
                "time_s": t_par,
                "speedup": round(sp, 4),
                "efficiency_pct": round(eff, 2),
            }
        )

        with ProcessPoolExecutor(max_workers=p) as pool:
            step5_parallel.warm_pool(pool, p)
            t0 = time.perf_counter()
            step5_parallel.simulate_replicas_in_pool(
                pool, n, arrival_rate, SERVICE_RATE_DEFAULT, servers, seeds, return_metrics=True
            )
            t_warm = time.perf_counter() - t0
        sp_w = t_serial / t_warm if t_warm > 0 else 0.0
        records.append(
            {
                "workers": p,
                "mode": "parallel_warm",
                "n": n,
                "servers": servers,
                "replicas": r_reps,
                "time_s": t_warm,
                "speedup": round(sp_w, 4),
                "efficiency_pct": round((sp_w / p) * 100.0, 2),
            }
        )
    return records


def export_csv(data: list[dict[str, Any]], filepath: Path) -> None:
    if not data:
        return
    filepath.parent.mkdir(parents=True, exist_ok=True)
    keys = list(data[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


def run_all_benchmarks(
    mode: str = "quick", output_dir: str = "results/raw"
) -> dict[str, Any]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = get_profile(mode)
    print(f"=== Iniciando benchmarks (Perfil: {profile.name.upper()}) ===")

    save_env_info(out_dir)

    print("-> Calculando metricas de codigo con radon...")
    code_metrics = compute_code_metrics()
    with open(out_dir / "code_metrics.json", "w", encoding="utf-8") as f:
        json.dump(code_metrics, f, indent=2, ensure_ascii=False)

    print("-> Midiendo memoria pico con tracemalloc...")
    mem_records = measure_memory(profile)
    export_csv(mem_records, out_dir / "benchmark_memory.csv")

    print("-> Midiendo tiempos de ejecucion (interleaved)...")
    time_records = measure_times(profile)
    export_csv(time_records, out_dir / "benchmark_times.csv")

    print("-> Midiendo escalamiento paralelo (escalon 5)...")
    scaling_records = measure_parallel_scaling(profile)
    export_csv(scaling_records, out_dir / "parallel_scaling.csv")

    print(f"=== Mediciones completadas y guardadas en {out_dir} ===")
    return {
        "profile": profile.name,
        "code_metrics": code_metrics,
        "time_records": time_records,
        "mem_records": mem_records,
        "scaling_records": scaling_records,
    }
