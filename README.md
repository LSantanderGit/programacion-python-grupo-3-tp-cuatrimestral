# Escalera de Optimización en Python: Simulador de Colas Monte Carlo

Trabajo de investigación grupal de la asignatura **T1-23-88xT1-23-28 PROGRAMACIÓN EN PYTHON** (Facultad de Tecnología Informática, Universidad Abierta Interamericana - UAI, Sede: 093 UAI - NORTE, Turno Noche, Grupo 3).

### Integrantes
- José Manuel Balderrama Mariscal
- Ramiro Busto
- Micaela Escobar Lyon
- Nicolas Torcuato Alberto Maciel
- Lucas Matías Santander

**Profesores:**
- Ing. Gastón Matías Weingand
- Ing. Bonaccorsi Maximiliano Leonardo  

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

### 3. Ejecutar la Pipeline Automatizada (Todo-en-Uno)
El script [scripts/run_all.py](file:///c:/Users/lsantander/Documents/uai/python/Tp/programacion-python-grupo-3-tp-cuatrimestral/scripts/run_all.py) es el punto de entrada integral que en una sola pasada ejecuta los tests, mide rendimiento y memoria, genera las figuras a 300 DPI, construye el informe formal y el Dashboard web interactivo:

- **Modo rápido Todo-en-Uno con Dashboard en vivo (`--serve`):**
  ```bash
  uv run python -m scripts.run_all --mode quick --serve
  ```
  *(Corre los tests, benchmarks, genera gráficos/reportes y abre automáticamente el Dashboard interactivo en el navegador)*.

- **Modo rápido estándar (Quick, ~1 a 2 minutos):**
  ```bash
  uv run python -m scripts.run_all --mode quick
  ```

- **Modo completo (Full):** Ejecución exhaustiva con tamaños de hasta $10^7$ solicitudes y repeticiones intercaladas para el informe formal:
  ```bash
  uv run python -m scripts.run_all --mode full
  ```

### 4. Servir el Dashboard Web en cualquier momento
Si los benchmarks ya fueron ejecutados previamente, se puede levantar directamente el servidor web interactivo sin volver a correr las pruebas:
```bash
uv run python -m scripts.serve_dashboard
```
El dashboard estará accesible localmente en `http://localhost:8000/results/dashboard.html`.

### 5. Benchmark de Humo (CI)
Para verificar que no existan regresiones de rendimiento en entornos de integración continua mediante ratios relativos (sin falsos positivos por ruido en runners compartidos):
```bash
uv run python -m scripts.smoke_benchmark
```

### 6. Verificación de Linter y Formato
```bash
uv run ruff check .
```

---

## Documentación y Referencias
- [docs/CONTEXTO.md](file:///c:/Users/lsantander/Documents/uai/python/Tp/programacion-python-grupo-3-tp-cuatrimestral/docs/CONTEXTO.md): Contexto y consigna del trabajo de investigación.
- [docs/decisiones.md](file:///c:/Users/lsantander/Documents/uai/python/Tp/programacion-python-grupo-3-tp-cuatrimestral/docs/decisiones.md): Registro histórico de decisiones técnicas cerradas (D1 a D23).
- [docs/diferencias_y_decisiones_proyecto.md](file:///c:/Users/lsantander/Documents/uai/python/Tp/programacion-python-grupo-3-tp-cuatrimestral/docs/diferencias_y_decisiones_proyecto.md): Informe exhaustivo de evolución, diferencias respecto al prompt inicial y justificación de decisiones.
- [docs/hallazgos_fase3.md](file:///c:/Users/lsantander/Documents/uai/python/Tp/programacion-python-grupo-3-tp-cuatrimestral/docs/hallazgos_fase3.md): Detalle empírico de las mediciones de Numba, warm-up y escalamiento paralelo.
- [docs/propuesta_presentacion.md](file:///c:/Users/lsantander/Documents/uai/python/Tp/programacion-python-grupo-3-tp-cuatrimestral/docs/propuesta_presentacion.md): Estructura y notas para la presentación oral ante la cátedra.
