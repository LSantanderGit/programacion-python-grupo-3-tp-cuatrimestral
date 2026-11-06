# Prompt inicial para Claude Code: "Escalera de optimización" (queue-perf-ladder)

> Creado el 2026-11-06. Entrega del trabajo: **jueves 19/11/2026**. Repositorio en GitHub. Informe en Google Docs. PC de mediciones: Windows 10, Intel Core i9 de 13.ª generación, 32 GB DDR5.

## 1. Decisiones técnicas ya cerradas (Claude Code las guarda en `docs/decisiones.md`)

| # | Decisión | Detalle |
|---|---|---|
| D1 | Algoritmo para c servidores | Cada request va al worker que se libera primero: `inicio = max(llegada, min(libres))`, `libres[argmin] = inicio + servicio`. Lindley (`W[i+1] = max(0, W[i] + S[i] - A[i+1])`) solo vale para c=1. |
| D2 | Baseline | **Por eventos**, ingenuo pero razonable: objeto `Request` por llegada, listas, búsqueda lineal del worker libre. **No** reloj discretizado (agrega error de discretización contra la teoría). Debe documentarse por qué no es un hombre de paja. |
| D3 | Contrato de `simulate` | `simulate(arrivals, services, servers) -> waits` (array de esperas en cola, uno por request). Las métricas (media, p95, utilización) las calcula una función común `metrics()` con la misma definición de percentil para todos los escalones. Se mide `simulate` por separado de `metrics`. |
| D4 | Criterio de corrección | Entre escalones y baseline: `numpy.allclose` con `rtol=1e-9`. Contra teoría: criterio estadístico (dentro de ~3 errores estándar sobre R réplicas). |
| D5 | Régimen de operación | ρ entre 0,5 y 0,8 para validar; descartar transitorio inicial (p. ej. primeros 5 % de requests). Un barrido ρ = 0,5 a 0,9 solo en el experimento de capacity planning. |
| D6 | Matriz de tamaños | Baseline y escalón 2: hasta 10⁶ (cortar antes si tarda demasiado, declararlo como limitación). Escalones 3, 4 y 5: hasta 10⁷. Se definen en `benchmarks/config.py`. |
| D7 | Paralelismo | Cada réplica genera sus entradas con una semilla hija (`SeedSequence.spawn`). El speedup se calcula contra **las mismas R réplicas en serie con el escalón 4**, no contra el escalón 0. Compatibilidad con Windows (`spawn`): todo bajo `if __name__ == "__main__"`, funciones top-level, `ProcessPoolExecutor`. |
| D8 | CPU híbrida (i9 13.ª gen: núcleos P y E) | La curva de eficiencia no será lineal. Medir con 1, 2, 4, 8, 16 y N lógicos; reportar el codo de la curva y discutirlo en la sección Discusión. `env.json` registra el modelo exacto de CPU. |
| D9 | CI en GitHub Actions | Matriz `ubuntu-latest` + `windows-latest`, Python 3.12. Corre `ruff`, `pytest` y un benchmark de humo. La regresión de rendimiento se verifica con **ratios** (p. ej. escalón 4 al menos X veces más rápido que escalón 1), nunca con tiempos absolutos, porque los runners compartidos son ruidosos. |
| D10 | Idioma | Documentación, README, docstrings, comentarios y mensajes en **español**. Identificadores de código en inglés. |
| D11 | Alcance | Sin escalón 6 y sin segundo caso de estudio. Dashboard HTML (plotly) solo si sobra tiempo al final, generado desde `results/raw/`. |
| D12 | Informe | Se arma en **Google Docs**. `make_report.py` genera: figuras PNG a 300 dpi tituladas como "Gráfico 1, 2, ..." (arábigos), tablas en markdown/CSV tituladas "Tabla I, II, ..." (romanos) y un borrador por capítulo en `report/` siguiendo el orden de la guía UAI. |

## 2. Prompt inicial (Fases 0 y 1)

Copiar desde la línea siguiente hasta el final de esta sección.

```
Sos el desarrollador principal de "queue-perf-ladder", un trabajo de investigación grupal de la UAI (Programación II) sobre rendimiento en Python. Respondé siempre en español.

OBJETIVO DE ESTA SESIÓN: ejecutar las Fases 0 y 1 y detenerte para que revise el equipo. No avances a la Fase 2.

LEÉ PRIMERO, en este orden:
1. docs/CONTEXTO.md (contexto completo del proyecto; lo marcado "Decidido" no se reabre).
2. Este prompt completo.

QUÉ ES EL PROYECTO (resumen): se mide cuánto se acelera un simulador de colas (N workers, requests con llegadas y servicios aleatorios, Monte Carlo) en cada escalón de optimización (0 baseline, 1 estructuras de datos, 2 Python idiomático, 3 NumPy, 4 Numba, 5 multiprocessing) y cuánto cuesta cada mejora en legibilidad y mantenibilidad. Cada versión debe dar el mismo resultado que el baseline y coincidir con la teoría de colas M/M/1 y M/M/c. Todo el código es Python. Se entrega el 19/11/2026.

DECISIONES TÉCNICAS CERRADAS (guardalas tal cual en docs/decisiones.md con el formato "D#: decisión, razón, fecha"):
- D1: para c servidores, cada request va al worker que se libera primero: inicio = max(llegada, min(libres)); libres[argmin] = inicio + servicio. Lindley solo vale para c=1.
- D2: el baseline es por eventos, ingenuo pero razonable (objeto Request por llegada, listas, búsqueda lineal del worker libre). No usar reloj discretizado. Documentar en el docstring por qué no es un hombre de paja.
- D3: contrato común: simulate(arrivals, services, servers) -> waits (np.ndarray de esperas en cola, uno por request). Las métricas (media de espera, tiempo medio en el sistema, p95, utilización) las calcula una función común metrics() en src/queue_sim/metrics.py, con la misma definición de percentil para todos los escalones.
- D4: corrección entre escalones y baseline con np.allclose(rtol=1e-9). Contra la teoría, criterio estadístico (dentro de ~3 errores estándar sobre R réplicas).
- D5: validar con rho entre 0.5 y 0.8 y descartar el transitorio inicial (parámetro, por defecto 5 %).
- D7, D8, D9, D10, D11, D12: ver CLAUDE.md que vas a crear; D6 se implementa en la Fase 4.

FASE 0: SETUP (criterio de salida: `uv sync` y `uv run pytest` corren en limpio en Windows 10)
1. Crear la estructura de repo de docs/CONTEXTO.md sección 5, más: src/queue_sim/metrics.py, docs/decisiones.md, report/ (vacío con .gitkeep), .gitignore (incluir .venv, __pycache__, results/raw/ NO se ignora), .github/workflows/ci.yml.
2. Python 3.12. Dependencias con uv (pyproject.toml + uv.lock): numpy, numba, pytest, pytest-benchmark, ruff, radon, matplotlib, pandas, psutil, py-cpuinfo. Resolvé versiones de numpy y numba compatibles entre sí y con Python 3.12, y fijalas. Si alguna instalación falla en Windows, avisame en vez de buscar atajos.
3. Crear CLAUDE.md en la raíz con el contenido de la sección "CLAUDE.md" que está al final de este prompt.
4. ci.yml: matriz ubuntu-latest y windows-latest, Python 3.12, uv sync, ruff check, pytest. Todavía sin benchmarks.
5. README.md mínimo con "cómo replicar" (instalar uv, uv sync, uv run pytest). Se completa en fases posteriores.

FASE 1: BASELINE Y ORÁCULO (criterio de salida: tests en verde y baseline validado contra la teoría)
1. workload.py: generate_workload(n_requests, arrival_rate, service_rate, seed) -> (arrivals, services) usando np.random.default_rng(seed). arrivals son tiempos absolutos de llegada (cumsum de interarribos exponenciales); services son duraciones exponenciales. Función auxiliar spawn_seeds(seed, n) con SeedSequence.spawn.
2. theory.py: M/M/1 (rho, Wq, W) y M/M/c con Erlang C (rho, probabilidad de espera, Wq, W). Validar entradas (lambda < c*mu) y lanzar ValueError con mensaje en español.
3. metrics.py: metrics(waits, services, servers, makespan=None, warmup_frac=0.05) -> dict con mean_wait, mean_sojourn, p95_wait, p95_sojourn, utilization. Usar np.percentile con el método por defecto, documentado.
4. step0_naive.py: simulate(arrivals, services, servers) -> waits, según D1 y D2. Tipado completo y docstring en español.
5. Tests (tests/): 
   - test_theory.py: casos conocidos de M/M/1 y de M/M/c (c=1 de M/M/c coincide con M/M/1; un caso c=2 verificable a mano o por identidad).
   - test_workload.py: reproducibilidad por semilla y estadística de las exponenciales.
   - test_step0.py: (a) caso determinista chico calculado a mano (por ejemplo 5 requests con valores fijos y c=1 y c=2); (b) contra la teoría con R=20 réplicas, n=200_000, rho=0.7, c=1 y c=3, criterio estadístico de D4; (c) invariantes: espera >= 0, mismo resultado con la misma semilla.
   - Parametrizá los tests de corrección con una lista STEPS = [step0.simulate] para que en las fases siguientes sólo se agreguen escalones.
6. Verificá con `uv run pytest -q` y `uv run ruff check .`. Hacé un commit por cada bloque lógico (setup, workload+theory, metrics, step0+tests) con mensajes en español, formato "feat:", "test:", "chore:", "docs:".

AL TERMINAR, entregá un reporte corto con: qué quedó hecho, resultado de pytest y ruff, la comparación numérica del baseline contra la teoría (tabla: configuración, valor teórico, valor simulado, error estándar), tiempo del baseline para n=10^5 y 10^6 en esta máquina, y cualquier ambigüedad o decisión que tomaste y no esté en este prompt (anotala en docs/decisiones.md). Después detenete y esperá instrucciones.

REGLAS DE TRABAJO:
- La corrección va antes que la velocidad. No avances si un test falla.
- Si algo no está definido, elegí la opción más simple, anotala en docs/decisiones.md y seguí. Frená y preguntame sólo si la decisión cambia el diseño de varios módulos.
- No agregues dependencias fuera de la lista ni escalones fuera de alcance (sin Cython/Rust, sin segundo caso de estudio).
- No inventes resultados ni números de rendimiento: todo número que reportes debe salir de una ejecución real.
- No uses generadores aleatorios propios dentro de los escalones; las entradas siempre vienen de workload.py.

=== CLAUDE.md (contenido para crear en la raíz del repo) ===

# queue-perf-ladder

Trabajo de investigación UAI (69 - Optativa - Programación II): "Escalera de optimización en Python". Contexto completo en docs/CONTEXTO.md; decisiones técnicas en docs/decisiones.md. Entrega: 19/11/2026.

## Reglas permanentes
- Responder y documentar en español (docstrings, comentarios, README, mensajes de commit). Identificadores de código en inglés.
- Python 3.12, dependencias con uv (pyproject.toml + uv.lock). Comandos: `uv sync`, `uv run pytest -q`, `uv run ruff check .`, `uv run python -m scripts.run_all --mode quick|full`.
- Todos los escalones implementan `simulate(arrivals, services, servers) -> waits` y reciben las mismas entradas generadas por `workload.py` con `np.random.default_rng(seed)`. Prohibido crear generadores aleatorios dentro de los escalones. Las réplicas paralelas usan `SeedSequence.spawn`.
- La corrección va primero: cada escalón se valida contra el baseline (`allclose`, rtol=1e-9) y contra la teoría (`theory.py`, criterio estadístico) antes de medir su tiempo.
- Algoritmo para c servidores: asignar al worker que se libera primero. Lindley sólo para c=1.
- Mediciones: `time.perf_counter()`, descartar warm-up de Numba (medirlo aparte), 7 a 30 repeticiones, reportar mediana y rango intercuartil, orden de pruebas intercalado. Cada corrida guarda `env.json` (CPU exacta, núcleos físicos y lógicos, RAM, SO, versiones de Python, NumPy, Numba).
- Los benchmarks escriben datos crudos en `results/raw/`; `scripts/make_report.py` regenera tablas y figuras sin volver a medir.
- Resultados centrales en speedup y tendencias, nunca tiempos absolutos como conclusión general. Tablas numeradas en romanos (Tabla I, II...), gráficos en arábigos (Gráfico 1, 2...).
- Multiprocessing compatible con Windows: código bajo `if __name__ == "__main__"`, funciones a nivel de módulo, `ProcessPoolExecutor`.
- Portabilidad: Windows, Linux, macOS. El punto de entrada es un script de Python, no `make`.
- CI (GitHub Actions): ruff + pytest + benchmark de humo; la regresión de rendimiento se verifica con ratios entre escalones, nunca con tiempos absolutos.
- Sin dependencias difíciles de instalar en el camino principal. Lo "Decidido" en docs/CONTEXTO.md no se reabre sin pedido explícito del grupo.
- Todo número en informes o README debe provenir de una ejecución real. No inventar resultados.
- Registrar en docs/decisiones.md cada decisión nueva (D#, decisión, razón, fecha).
- Commits chicos y frecuentes, en español, con prefijos feat:/test:/fix:/docs:/chore:.
```

## 3. Prompts siguientes (uno por fase, cortos)

**Fase 2: escalones 1 a 3.** "Leé CLAUDE.md y docs/decisiones.md. Implementá step1_datastructs.py (deque, heapq, `__slots__`), step2_idiomatic.py (variables locales, menos llamadas) y step3_numpy.py (generación en bloque; para c=1 probá la recurrencia de Lindley con trucos de `np.maximum.accumulate` y documentá si funciona y por qué no para c>1). Agregalos a STEPS en los tests y pasá la validación contra baseline y teoría. Un commit por escalón. Medí un tiempo rápido de cada uno con n=10^5 y reportá speedup contra baseline y contra el escalón anterior. Detenete al terminar."

**Fase 3: escalones 4 y 5.** "Implementá step4_numba.py (`@njit(cache=True)`, array de tiempos libres con argmin) y step5_parallel.py (réplicas Monte Carlo con ProcessPoolExecutor, semillas con SeedSequence.spawn, compatible con Windows). Medí el warm-up de Numba aparte. Validá contra baseline y teoría. Reportá speedup y eficiencia con 1, 2, 4, 8, 16 y N procesos contra las mismas R réplicas en serie con el escalón 4. Detenete al terminar."

**Fase 4: harness y automatización.** "Implementá benchmarks/harness.py, benchmarks/env_info.py, benchmarks/config.py (matriz de tamaños D6), medición de memoria con tracemalloc, métricas de mantenibilidad con radon (líneas, complejidad ciclomática, dependencias nuevas por escalón) y scripts/run_all.py con --mode quick (2 a 3 minutos) y --mode full. Agregá el benchmark de humo con ratios al CI. Completá el README con 'cómo replicar'. Verificá que `quick` funciona de punta a punta."

**Fase 5: corridas finales y reporte.** "Voy a correr `--mode full` en la PC de mediciones (Windows 10, i9, 32 GB). Implementá scripts/make_report.py: figuras PNG 300 dpi (tiempo vs tamaño, speedup por escalón, speedup vs costo de mantenimiento, curva de eficiencia y Amdahl, error vs teoría), tablas en markdown con numeración romana y borradores en report/ por capítulo de la guía UAI (Resultados con tablas y gráficos y su análisis; el resto como esqueleto con los datos del proyecto). No escribas conclusiones que los datos no sostengan."

**Fase 6: informe y presentación (yo, con apoyo de Claude en el chat).** Armar el informe en Google Docs (hoja carta, doble espacio, márgenes 4/4/4/2,5 cm, numeración arriba a la derecha desde la Introducción), actualizar la presentación con las figuras reales y hacer la prueba de replicabilidad en otra PC.

## 4. Cronograma tentativo hasta el 19/11

| Fecha | Trabajo |
|---|---|
| Sáb 7 y dom 8/11 | Fase 0 y 1. En paralelo, borrador de Introducción y Aspectos teóricos |
| Lun 9 y mar 10/11 | Fase 2 |
| Mié 11/11 | Fase 3 |
| Jue 12/11 | Fase 4 |
| Vie 13 y sáb 14/11 | Fase 5: corridas finales (PC sin otros programas, plan de energía en alto rendimiento) y figuras |
| Dom 15 a mar 17/11 | Informe en Google Docs (Resultados, Discusión, Conclusiones, Sugerencias, Resumen, Referencias) y presentación |
| Mié 18/11 | Prueba de replicabilidad en otra PC, ensayo de la presentación, revisión final |
| Jue 19/11 | Entrega |

Si algo se atrasa, se recorta en este orden: dashboard HTML, memoria con tracemalloc, tamaño 10⁷ en escalones lentos. No se recorta la validación de corrección ni la replicabilidad.
