"""Punto de entrada unico para la reproduccion automatizada del proyecto.

Uso:
    python -m scripts.run_all --mode quick
    python -m scripts.run_all --mode full
    python -m scripts.run_all --mode quick --serve
"""

import argparse
import sys
from pathlib import Path

import pytest
from benchmarks.env_info import get_env_info
from benchmarks.harness import run_all_benchmarks

from scripts.make_dashboard import generate_dashboard_html
from scripts.make_report import main as generate_report_and_figures
from scripts.serve_dashboard import serve_dashboard


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Punto de entrada integral para pruebas, benchmarks, reportes y dashboard de queue-perf-ladder."
    )
    parser.add_argument(
        "--mode",
        choices=["quick", "full"],
        default="quick",
        help="Modo de ejecucion: 'quick' (2-3 min) o 'full' (corrida exhaustiva para el informe).",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Omite la ejecucion de la suite de pruebas unitarias (no recomendado).",
    )
    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="Omite la generacion automatica de figuras a 300 DPI y capitulos del informe.",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Inicia un servidor HTTP local y abre automaticamente el Dashboard web en el navegador.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/raw",
        help="Directorio de destino para los archivos CSV/JSON crudos.",
    )
    return parser.parse_args()


def print_summary(env: dict, results: dict) -> None:
    """Imprime un resumen formateado de los resultados en la terminal."""
    print("\n" + "=" * 70)
    print("                    RESUMEN DE RESULTADOS")
    print("=" * 70)
    print(f"Entorno: CPU {env.get('cpu_brand')} | {env.get('cpu_physical_cores')} fisicos / {env.get('cpu_logical_cores')} logicos")
    print(f"SO: {env.get('os_system')} {env.get('os_release')} | Python: {env.get('python_version')} | Numba: {env.get('numba_version')}")
    print(f"Perfil ejecutado: {results['profile'].upper()}")

    # Metricas de software
    print("\n--- Metricas de Codigo (radon) ---")
    print(f"{'Escalon':<20} | {'SLOC':<6} | {'CC Media':<10} | {'CC Max':<8} | Dependencias")
    print("-" * 70)
    for m in results["code_metrics"]:
        deps = ", ".join(m["new_dependencies"]) if m["new_dependencies"] else "ninguna"
        print(f"{m['step']:<20} | {m['sloc']:<6} | {m['avg_complexity']:<10} | {m['max_complexity']:<8} | {deps}")

    # Tiempos representativos
    print("\n--- Tiempos y Speedup representativos (servers=2) ---")
    records_c2 = [r for r in results["time_records"] if r["servers"] == 2]
    sizes = sorted({r["n"] for r in records_c2})
    
    for n in sizes:
        print(f"\n[ Tamano n = {n:,} ]")
        step0_rec = next((r for r in records_c2 if r["n"] == n and r["step"] == "step0_naive"), None)
        base_time = step0_rec["median_s"] if step0_rec else None

        for r in records_c2:
            if r["n"] == n:
                med_ms = r["median_s"] * 1000
                iqr_ms = r["iqr_s"] * 1000
                sp_str = f"{base_time / r['median_s']:6.2f}x" if base_time and r["median_s"] > 0 else "  N/A  "
                print(f"  {r['step']:<20}: {med_ms:8.2f} ms (+/- {iqr_ms:6.2f} ms) | Speedup vs Base: {sp_str}")

    # Escalamiento paralelo
    print("\n--- Escalamiento Paralelo (Escalon 5 vs Escalon 4 Serie) ---")
    print(f"{'Procesos':<10} | {'Tiempo (s)':<12} | {'Speedup':<10} | {'Eficiencia':<10}")
    print("-" * 50)
    for s in results["scaling_records"]:
        mode_label = "Serie (E4)" if s["workers"] == 0 else f"{s['workers']} proc"
        print(f"{mode_label:<10} | {s['time_s']:10.4f} s | {s['speedup']:8.2f}x | {s['efficiency_pct']:8.1f}%")

    print("\n" + "=" * 70)
    print(f"Datos crudos persistidos en: {Path(results.get('output_dir', 'results/raw')).resolve()}")
    print("=" * 70 + "\n")


def main() -> int:
    args = parse_args()

    # 1. Tests de correccion primero
    if not args.skip_tests:
        print("\n[Paso 1/4] Ejecutando suite de verificacion y correccion (pytest)...")
        exit_code = pytest.main(["-q"])
        if exit_code != 0:
            print(f"\n[ERROR] Los tests fallaron (codigo {exit_code}). Abortando benchmarks por principio de correccion.", file=sys.stderr)
            return exit_code
        print("[OK] Todos los tests de correccion pasaron exitosamente.\n")
    else:
        print("[ADVERTENCIA] Omitiendo tests de correccion segun solicitud.\n")

    # 2. Ejecutar benchmarks
    print(f"[Paso 2/4] Ejecutando bateria de benchmarks (modo '{args.mode}')...")
    env = get_env_info()
    results = run_all_benchmarks(mode=args.mode, output_dir=args.output_dir)
    results["output_dir"] = args.output_dir

    # 3. Mostrar resumen en terminal
    print_summary(env, results)

    # 4. Generar reportes y dashboard web
    if not args.skip_report:
        print("[Paso 3/4] Generando figuras PNG (300 DPI) y capitulos del informe...")
        generate_report_and_figures()
        print("[Paso 4/4] Construyendo Dashboard Web Interactivo...")
        dashboard_path = Path("results/dashboard.html")
        generate_dashboard_html(Path(args.output_dir), dashboard_path)
        print(f"[OK] Dashboard listo en: {dashboard_path.resolve()}\n")

    # 5. Servir dashboard si se solicito
    if args.serve:
        print("-> Iniciando servidor web para el Dashboard interactivo...")
        serve_dashboard()

    return 0


if __name__ == "__main__":
    sys.exit(main())
