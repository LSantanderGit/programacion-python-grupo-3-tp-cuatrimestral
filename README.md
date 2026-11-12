# Escalera de Optimización en Python: Simulador de Colas Monte Carlo

Trabajo de investigación grupal de la asignatura **69 - Optativa - Programación II** (Facultad de Tecnología Informática, Universidad Abierta Interamericana - UAI, Sede Norte, Turno Noche, Grupo 3).

### Integrantes
- José Manuel Balderrama Mariscal
- Ramiro Busto
- Micaela Escobar Lyon
- Nicolas Torcuato Alberto Maciel
- Lucas Matías Santander

**Profesor Titular:** Ing. Gastón Matías Weingand  
**Fecha de entrega:** 19/11/2026  

---

## Descripción del Proyecto

El trabajo investiga empíricamente cómo se acelera un sistema secuencial en Python etapa por etapa (la **"escalera de optimización"**) y evalúa el costo de cada peldaño en complejidad ciclomática, líneas de código y dependencias.

Como caso de estudio de *capacity planning*, se implementa un simulador de colas por eventos con $c$ servidores de atención paralela y llegadas/servicios aleatorios (simulación Monte Carlo). Cada escalón implementa la misma interfaz común `simulate(arrivals, services, servers) -> waits` y se valida rigurosamente contra el baseline y contra las soluciones analíticas de la teoría de colas ($M/M/1$ y $M/M/c$ con fórmula de Erlang C).

### Los Escalones de la Escalera
- **Escalón 0 (Baseline ingenuo):** Python puro con objetos `Request`, cola como lista y búsqueda lineal del servidor libre.
- **Escalón 1 (Estructuras de datos):** `collections.deque`, `heapq` para los instantes de liberación y `__slots__`.
- **Escalón 2 (Python idiomático):** Variables locales en el bucle caliente, iteración directa sobre listas nativas y `heapreplace`.
- **Escalón 3 (NumPy):** Vectorización en bloque de llegadas y servicios; recurrencia de Lindley vectorizada para $c=1$.
- **Escalón 4 (Numba JIT):** Compilación nativa con `@njit(cache=True)` y selección mediante `argmin`.
- **Escalón 5 (Paralelismo):** Réplicas Monte Carlo independientes distribuidas con `ProcessPoolExecutor` y semillas derivadas con `SeedSequence.spawn`.

---

## Cómo Replicar el Proyecto

El entorno está completamente gestionado y bloqueado con **[uv](https://docs.astral.sh/uv/)**. No se requiere compilador de C ni herramientas externas adicionales.

### 1. Clonar e Instalar Dependencias
```bash
git clone https://github.com/LSantanderGit/programacion-python-grupo-3-tp-cuatrimestral.git
cd programacion-python-grupo-3-tp-cuatrimestral

# Sincroniza el entorno virtual con Python 3.12 y las versiones fijadas en uv.lock
uv sync
```

### 2. Ejecutar Tests de Corrección
Valida que todas las implementaciones coincidan con el baseline (`allclose`, tolerancia $10^{-9}$) y cumplan el criterio estadístico contra las fórmulas teóricas:
```bash
uv run pytest -q
```

### 3. Ejecutar los Benchmarks Automatizados
El script [scripts/run_all.py](file:///c:/Users/lsantander/Documents/uai/python/Tp/programacion-python-grupo-3-tp-cuatrimestral/scripts/run_all.py) es el punto de entrada único para ejecutar pruebas, capturar el entorno del sistema, realizar mediciones de tiempo/memoria y generar las métricas de calidad de código con `radon`.

- **Modo rápido (Quick, ~1 a 2 minutos):** Ideal para verificación funcional y de rendimiento local:
  ```bash
  uv run python -m scripts.run_all --mode quick
  ```

- **Modo completo (Full):** Ejecución exhaustiva con tamaños de hasta $10^7$ solicitudes y repeticiones intercaladas para el informe formal:
  ```bash
  uv run python -m scripts.run_all --mode full
  ```

Los datos crudos generados (CSV y JSON) se guardan automáticamente en `results/raw/`:
- `results/raw/env.json`: Especificaciones completas de hardware (CPU, núcleos, RAM) y versiones.
- `results/raw/benchmark_times.csv`: Tiempos (mediana, IQR, min, max) por escalón, tamaño y servidores.
- `results/raw/benchmark_memory.csv`: Consumo de memoria pico (`tracemalloc`).
- `results/raw/parallel_scaling.csv`: Speedup y eficiencia del escalón paralelo.
- `results/raw/code_metrics.json`: Líneas de código (LOC/SLOC) y complejidad ciclomática (`radon`).

### 4. Benchmark de Humo (CI)
Para verificar que no existan regresiones de rendimiento en entornos de integración continua mediante ratios relativos (sin falsos positivos por ruido en runners compartidos):
```bash
uv run python -m scripts.smoke_benchmark
```

### 5. Verificación de Linter y Formato
```bash
uv run ruff check .
```

---

## Documentación y Referencias
- [docs/CONTEXTO.md](file:///c:/Users/lsantander/Documents/uai/python/Tp/programacion-python-grupo-3-tp-cuatrimestral/docs/CONTEXTO.md): Resumen del contexto y objetivos del proyecto.
- [docs/decisiones.md](file:///c:/Users/lsantander/Documents/uai/python/Tp/programacion-python-grupo-3-tp-cuatrimestral/docs/decisiones.md): Registro de decisiones técnicas cerradas (D1 a D19).
- [docs/hallazgos_fase3.md](file:///c:/Users/lsantander/Documents/uai/python/Tp/programacion-python-grupo-3-tp-cuatrimestral/docs/hallazgos_fase3.md): Detalle empírico de las mediciones de Numba, warm-up y escalamiento paralelo.
