# queue-perf-ladder

Trabajo de investigacion UAI (69 - Optativa - Programacion II): "Escalera de optimizacion en Python". Contexto en docs/CONTEXTO.md; decisiones tecnicas en docs/decisiones.md. Entrega: 19/11/2026.

## Reglas permanentes
- Responder y documentar en espanol (docstrings, comentarios, README, mensajes de commit). Identificadores de codigo en ingles.
- Python 3.12, dependencias con uv (pyproject.toml + uv.lock). Comandos: `uv sync`, `uv run pytest -q`, `uv run ruff check .`, `uv run python -m scripts.run_all --mode quick|full`.
- Todos los escalones implementan `simulate(arrivals, services, servers) -> waits` y reciben las mismas entradas generadas por `workload.py` con `np.random.default_rng(seed)`. Prohibido crear generadores aleatorios dentro de los escalones. Las replicas paralelas usan `SeedSequence.spawn`.
- La correccion va primero: cada escalon se valida contra el baseline (`allclose`, rtol=1e-9) y contra la teoria (`theory.py`, criterio estadistico) antes de medir su tiempo.
- Algoritmo para c servidores: asignar al worker que se libera primero. Lindley solo para c=1.
- Mediciones: `time.perf_counter()`, descartar warm-up de Numba (medirlo aparte), 7 a 30 repeticiones, reportar mediana y rango intercuartil, orden de pruebas intercalado. Cada corrida guarda `env.json` (CPU exacta, nucleos fisicos y logicos, RAM, SO, versiones de Python, NumPy, Numba).
- Los benchmarks escriben datos crudos en `results/raw/`; `scripts/make_report.py` regenera tablas y figuras sin volver a medir.
- Resultados centrales en speedup y tendencias, nunca tiempos absolutos como conclusion general. Tablas numeradas en romanos (Tabla I, II...), graficos en arabigos (Grafico 1, 2...).
- Multiprocessing compatible con Windows: codigo bajo `if __name__ == "__main__"`, funciones a nivel de modulo, `ProcessPoolExecutor`.
- Portabilidad: Windows, Linux, macOS. El punto de entrada es un script de Python, no `make`.
- CI (GitHub Actions): ruff + pytest + benchmark de humo; la regresion de rendimiento se verifica con ratios entre escalones, nunca con tiempos absolutos.
- Sin dependencias dificiles de instalar en el camino principal. Lo "Decidido" en docs/CONTEXTO.md no se reabre sin pedido explicito del grupo.
- Todo numero en informes o README debe provenir de una ejecucion real. No inventar resultados.
- Registrar en docs/decisiones.md cada decision nueva (D#, decision, razon, fecha).
- Commits chicos y frecuentes, en espanol, con prefijos feat:/test:/fix:/docs:/chore:.
