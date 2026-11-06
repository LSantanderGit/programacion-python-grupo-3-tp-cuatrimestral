# Contexto del proyecto

Trabajo de investigacion grupal UAI (Programacion II): se mide cuanto se acelera un simulador de colas (c workers, requests con llegadas y servicios aleatorios, Monte Carlo) en cada escalon de optimizacion:

0. baseline por eventos, 1. estructuras de datos, 2. Python idiomatico, 3. NumPy, 4. Numba, 5. multiprocessing.

Se evalua tambien el costo de cada mejora en legibilidad y mantenibilidad. Cada version debe coincidir con el baseline y con la teoria M/M/1 y M/M/c. Entrega: 19/11/2026. Decisiones en `decisiones.md`.

## Estructura del repo

```
src/queue_sim/   workload.py, theory.py, metrics.py, step0_naive.py ... step5_parallel.py
tests/           test_theory.py, test_workload.py, test_step0.py ...
benchmarks/      harness, env_info, config (Fase 4)
scripts/         run_all.py, make_report.py
docs/            CONTEXTO.md, decisiones.md
report/          borradores del informe
results/raw/     datos crudos de mediciones (versionados)
.github/workflows/ci.yml
```
