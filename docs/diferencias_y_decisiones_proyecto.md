# Informe de Evolución, Decisiones y Estado Actual del Proyecto

> **Asignatura:** T1-23-88xT1-23-28 PROGRAMACIÓN EN PYTHON  
> **Institución:** Universidad Abierta Interamericana (UAI) - Facultad de Tecnología Informática  
> **Sede:** 093 UAI - NORTE | **Turno:** Noche | **Grupo:** 3  
> **Profesores:** Ing. Gastón Matías Weingand e Ing. Bonaccorsi Maximiliano Leonardo  
> **Fecha límite de entrega:** 19/11/2026  
> **Integrantes:**  
> - José Manuel Balderrama Mariscal  
> - Ramiro Busto  
> - Micaela Escobar Lyon  
> - Nicolas Torcuato Alberto Maciel  
> - Lucas Matías Santander  

---

## 1. Resumen Ejecutivo y Estado Actual del Proyecto

El proyecto **"TP Cuatrimestral: Escalera de Optimización"** es un trabajo de investigación empírica enmarcado en la ingeniería del software. Su propósito central es medir cuantitativamente cuánto se acelera un simulador estocástico de colas de eventos discretos ($M/M/1$ y $M/M/c$) en cada etapa progresiva de optimización en Python (la "escalera de optimización"), y balancear dicha ganancia contra el costo de mantenimiento, líneas de código y complejidad ciclomática.

A la fecha, el proyecto se encuentra **100% completado en sus fases técnicas (Fases 0 a 5)**:
- **Suite de pruebas de corrección analítica:** 74 tests unitarios pasando al 100% en `pytest`, validando determinismo, invariantes, coincidencia con el baseline (`allclose`, tolerancia $10^{-9}$) y consistencia estadística contra las fórmulas de Erlang C.
- **Calidad de código y linters:** Formato y análisis estático con `ruff` aprobado sin advertencias ni errores.
- **Harness automatizado y reproducible:** Mide tiempo (mediana e IQR intercalado), memoria pico con `tracemalloc`, líneas lógicas y complejidad con `radon`.
- **Figuras y Reporte Formal:** Generador desacoplado `scripts/make_report.py` que produce 5 gráficos en PNG a 300 DPI y tablas formales en Markdown según la guía de presentación de la UAI.
- **Dashboard Web Interactivo y Servidor Local:** Generación de un dashboard HTML5 responsivo (`results/dashboard.html`) y servidor local autónomo integrado con la opción `--serve` en `scripts/run_all.py`.

---

## 2. Diferencias entre el Prompt Inicial y el Proyecto Final

A lo largo del ciclo de desarrollo se detectaron oportunidades de mejora, ajustes de datos de la cátedra y hallazgos empíricos que motivaron discrepancias constructivas respecto a lo bosquejado inicialmente en el prompt de arranque (`.claude/PROMPT_INICIAL_claude_code.md`):

| Aspecto | Prompt de Inicialización | Proyecto Final Implementado | Justificación del Cambio |
|---|---|---|---|
| **Nombre del Proyecto** | `queue-perf-ladder` | **TP Cuatrimestral: Escalera de Optimización** (`tp-cuatrimestral-escalera-optimizacion`) | Formalización académica para la presentación ante la facultad en español. |
| **Identificación de Asignatura** | `69 - Optativa - Programación II` | **T1-23-88xT1-23-28 PROGRAMACIÓN EN PYTHON** | Corrección del código oficial de la materia en el plan de estudios. |
| **Cuerpo Docente** | Únicamente Ing. Gastón Matías Weingand | **Ing. Gastón Matías Weingand e Ing. Bonaccorsi Maximiliano Leonardo** | Inclusión de ambos profesores a cargo de la comisión. |
| **Sede Institucional** | "Regional Norte" / "Sede Norte" | **093 UAI - NORTE** | Denominación exacta de la sede según los registros de la UAI. |
| **Terminología de Suma Acumulada** | Uso de la función `np.cumsum` | Reemplazo por **`np.add.accumulate`** y menciones a **"suma acumulada"** | Se evitó la fonética y connotación del término inglés, adoptando el método canónico de *ufuncs* de NumPy, que resulta además 100% simétrico con `np.minimum.accumulate`. |
| **Manejo de Salidas y Resultados en Git** | `results/raw/` se planeaba versionar | **`results/raw/*`, `results/figures/*`, `results/*.html` y `report/*` ignorados en `.gitignore`** | Regla de oro de Git: *"No versiones lo que tu código puede generar"*. Evita ensuciar el repositorio con especificaciones de una sola PC (`env.json`), conflictos de fusión y miles de líneas en commits. Se mantienen las carpetas con `.gitkeep`. |
| **Herramientas y Prompts de IA** | Archivos `CLAUDE.md` y `.claude/` en el árbol de Git | **Confinados exclusivamente al entorno local e ignorados en Git** | Separación entre el producto de software universitario y el andamiaje auxiliar de asistencia. |
| **Dashboard Web de Resultados** | Condicional *"solo si sobra tiempo"* | **Implementado al 100% con servidor local integrado y comando `--serve`** | Al completarse las fases antes de tiempo, se desarrolló una interfaz ejecutiva moderna con Tailwind CSS que permite proyectar los resultados en vivo durante la defensa del trabajo. |
| **Transmisión de Datos en Multiprocessing (Windows)** | Se asumía serializar arrays de tiempos de espera crudos por réplica | **Parámetro `return_metrics=True` en `step5_parallel.py`** | En Windows (`spawn`), transmitir arrays masivos (16 MB por réplica) por pipes IPC saturaba el ancho de banda y arruinaba el speedup. Computar las métricas en el worker redujo la transferencia a un diccionario liviano. |

---

## 3. Matriz Completa de Decisiones Técnicas (D1 a D23)

A continuación se detallan todas las decisiones arquitectónicas registradas en el proyecto y el fundamento de ingeniería de cada una:

### Decisiones Fundacionales de Diseño
- **D1 (Algoritmo para $c$ servidores):** Cada solicitud se asigna al servidor que se libera primero: $\text{inicio} = \max(\text{llegada}, \min(\text{libres}))$; $\text{libres}[\arg\min] = \text{inicio} + \text{servicio}$.  
  *Por qué:* La recurrencia de Lindley ($W_{i+1} = \max(0, W_i + S_i - A_{i+1})$) solo es matemáticamente válida para colas $M/M/1$. Para $c > 1$ se requiere mantener el vector de instantes libres.
- **D2 (Baseline honesto por eventos):** Implementación en Python puro orientada a objetos (`Request`), listas y búsqueda lineal.  
  *Por qué:* No utiliza un reloj discretizado (que añadiría error artificial de discretización frente a la teoría) ni es un "hombre de paja"; representa el código natural que escribiría un programador sin optimizar.
- **D3 (Contrato común de simulación):** Todos los escalones implementan estrictamente `simulate(arrivals, services, servers) -> waits`. El cálculo de estadísticas se desacopla en `metrics.py`.  
  *Por qué:* Garantiza la intercambiabilidad total de los módulos en los tests y aísla el tiempo de simulación del cálculo de métricas.
- **D4 (Criterio estricto de corrección):** Entre escalones y baseline se exige coincidencia numérica determinista vía `numpy.allclose(rtol=1e-9)`. Frente a las fórmulas analíticas de Erlang C, se aplica criterio estadístico dentro de 3 errores estándar ($|\Delta| \le 3\,\text{EE}$) sobre $R$ réplicas.  
  *Por qué:* La corrección precede a la velocidad; ninguna optimización es válida si desvía el resultado.
- **D5 (Régimen de operación y transitorio):** Carga del sistema fijada en $\rho = 0.70 - 0.75$ y descarte del 5% inicial por efecto transitorio (*warmup fraction*).  
  *Por qué:* Evita el sesgo de estado inicial vacío en simulaciones Monte Carlo.
- **D6 (Matriz de tamaños escalonada):** Escalones lentos (0, 1 y 2) limitados hasta $10^5$ o $10^6$ solicitudes; escalones rápidos (3, 4 y 5) escalando hasta $10^7$.  
  *Por qué:* Ejecutar $10^7$ en Python puro insumiría horas, sin aportar valor comparativo adicional frente a la asíntota.
- **D7 (Independencia de réplicas en paralelismo):** Semillas derivadas con `SeedSequence.spawn()`. La referencia de speedup para el Escalón 5 son las **mismas $R$ réplicas ejecutadas en serie con el Escalón 4**.  
  *Por qué:* Comparar el paralelismo contra el baseline ingenuo inflaría artificialmente el speedup (falacia clásica); debe compararse contra la mejor versión secuencial optimizada.
- **D8 (Captura de hardware heterogéneo):** Registro del modelo comercial de CPU, núcleos físicos y lógicos en `env.json`.  
  *Por qué:* En procesadores modernos (como los Intel con núcleos P y E o Hyper-Threading), la curva de Amdahl presenta un codo al pasar de núcleos físicos a lógicos.
- **D9 (Regresión de rendimiento en CI por ratios):** El pipeline de GitHub Actions verifica que el escalón 4 supere al escalón 1 por un factor relativo (mínimo $5\times$), nunca por segundos absolutos.  
  *Por qué:* Los *runners* virtuales compartidos de CI sufren variaciones de carga impredecibles; los ratios relativos son inmunes a ese ruido.
- **D10 (Convención idiomática):** Código, docstrings, README y comentarios en español; identificadores y nombres de variables en inglés.  
  *Por qué:* Buenas prácticas de ingeniería y requerimiento institucional de la UAI.
- **D11 (Alcance acotado):** Exclusión de extensiones en C/Rust (escalón 6) o segundo caso de estudio de logs.  
  *Por qué:* Priorizar un trabajo completo, medido rigurosamente y replicable antes que abarcar demasiado sin profundidad.
- **D12 (Informe formal desacoplado):** `make_report.py` genera figuras a 300 DPI y tablas en Markdown listas para el informe formal en Google Docs.  
  *Por qué:* Permite actualizar el texto y los gráficos sin tener que reejecutar benchmarks que insumen tiempo.

### Decisiones de Implementación y Fases Sucesivas
- **D13 (Estructura de contexto unificada):** Se reemplazó el archivo resumido por la especificación canónica completa en `docs/CONTEXTO.md`.
- **D14 (Entorno bloqueado):** Python fijado en `3.12` mediante `uv.lock`, con NumPy 2.5 y Numba 0.68.
- **D15 (Cálculo de utilización y función makespan):** `metrics()` calcula utilización sobre la duración total del experimento agregando la función auxiliar `makespan(arrivals, waits, services)`.
- **D16 (Parámetros del oráculo analítico):** Validación contra Erlang C parametrizada con $\rho=0.70, \mu=1.0, n=200\,000, R=20$ réplicas y semilla 2026.
- **D17 (Límite de vectorización de Lindley en NumPy):** Se documentó formalmente que para $c=1$, Lindley vectoriza con `np.add.accumulate` y `np.minimum.accumulate`, pero para $c > 1$ el vector de servidores con `argmin` no admite scan simple y debe reutilizar el bucle con heap.
- **D18 (Desacoplamiento de Warm-up en Numba):** Se implementó `step4_numba.warmup()` para forzar la compilación JIT previamente y aislar el tiempo de LLVM del cronómetro de simulación.
- **D19 (Mitigación del cuello de botella IPC en Windows):** En `step5_parallel.py`, se añadió `return_metrics=True` para que los procesos trabajadores calculen localmente las métricas estadísticas y transmitan únicamente un diccionario liviano, evitando la serialización de arrays masivos por pipes IPC.
- **D20 (Perfiles de medición Quick y Full):** En `benchmarks/config.py`, se definió `quick` ($n \le 10^5$, 3 repeticiones, $<2$ minutos) y `full` ($n \le 10^7$, 7 repeticiones) junto con la extracción de SLOC y complejidad ciclomática mediante `radon`.
- **D21 (Smoke benchmark de regresión en CI):** `scripts/smoke_benchmark.py` asegura que Numba sea al menos $5.0\times$ más veloz que las estructuras de datos (en la práctica da $>100\times$).
- **D22 (Generación científica de figuras y tablas):** `scripts/make_report.py` aplica estándares tipográficos y de visualización a 300 DPI (Gráficos 1 a 5 y Tablas I a VI).
- **D23 (Dashboard Web Interactivo y flag `--serve`):** Creación de `scripts/make_dashboard.py` y `scripts/serve_dashboard.py`, unificando en `scripts/run_all.py --serve` la ejecución de pruebas, benchmarks, reportes y visualización en el navegador en un único comando.

---

## 4. Hallazgos Empíricos Clave del Proyecto

1. **El salto de Numba ($>130\times$ de aceleración):**
   Numba representó el hito más significativo de la escalera. Compilar el bucle secuencial a instrucciones de máquina nativas con LLVM redujo el tiempo de $50\,000$ eventos de $67.9\text{ ms}$ (baseline) a solo **$0.46\text{ ms}$**, con un impacto mínimo en mantenibilidad (31 líneas de código y complejidad ciclomática media de solo 1.67).
2. **La limitación intrínseca de NumPy en colas concurrentes ($c > 1$):**
   NumPy demostró ser imbatible para operaciones vectoriales independientes o acumulaciones lineales ($c=1$). Sin embargo, ante la necesidad de actualizar dinámicamente un estado de $c$ servidores mediante `argmin`, la vectorización en bloque se quiebra, demostrando que *"vectorizar no siempre es posible cuando existe dependencia temporal de estado"*.
3. **El costo del multiprocessing en Windows (`spawn`):**
   La creación de procesos en Windows toma entre $2$ y $3$ segundos. En tareas pequeñas o medianas, el tiempo de inicialización de intérpretes y serialización de memoria anula la ganancia. El paralelismo solo resulta rentable para simulaciones pesadas ($n \ge 10^6$), donde el speedup escala de manera casi lineal con 2 procesos ($1.81\times$, $90.7\%$ de eficiencia) y encuentra su meseta física en los 6 núcleos de la CPU ($2.50\times$), degradándose si se saturan los 12 hilos lógicos por contención en caché L3.

---

## 5. Estructura Limpia del Repositorio

El repositorio versiona exclusivamente código fuente, configuración y documentación:
```text
├── .github/workflows/ci.yml         # CI multiplataforma (Ubuntu + Windows) con smoke benchmark
├── .gitignore                       # Reglas limpias (ignora caches, IA y salidas dinámicas)
├── README.md                        # Portada institucional y guía de replicación rápida
├── pyproject.toml / uv.lock         # Dependencias reproducibles bloqueadas con uv
├── benchmarks/
│   ├── config.py                    # Matriz de tamaños y perfiles (quick / full)
│   ├── env_info.py                  # Detección automática de hardware y SO (env.json)
│   └── harness.py                   # Medición con time.perf_counter, tracemalloc y radon
├── docs/
│   ├── CONTEXTO.md                  # Contexto y consigna original del trabajo
│   ├── decisiones.md                # Registro histórico de decisiones D1 a D23
│   ├── hallazgos_fase3.md           # Informe de mediciones de Numba y paralelismo
│   ├── propuesta_presentacion.md    # Estructura de diapositivas para la defensa oral
│   └── diferencias_y_decisiones_proyecto.md # Este documento de contexto global
├── scripts/
│   ├── make_dashboard.py            # Generador del Dashboard Web interactivo (results/dashboard.html)
│   ├── make_report.py               # Generador de figuras a 300 DPI y capítulos del informe
│   ├── run_all.py                   # Orquestador Todo-en-Uno (tests, benchmarks, UI con --serve)
│   ├── serve_dashboard.py           # Servidor HTTP local autónomo para el navegador
│   └── smoke_benchmark.py           # Benchmark de humo para verificación de CI
├── src/queue_sim/
│   ├── metrics.py                   # Métricas estadísticas y cálculo de makespan
│   ├── step0_naive.py               # Escalón 0: Baseline ingenuo por eventos
│   ├── step1_datastructs.py         # Escalón 1: Deque, heapq y __slots__
│   ├── step2_idiomatic.py           # Escalón 2: Python idiomático y variables locales
│   ├── step3_numpy.py               # Escalón 3: NumPy (add.accumulate para c=1)
│   ├── step4_numba.py               # Escalón 4: Numba JIT (@njit(cache=True))
│   ├── step5_parallel.py            # Escalón 5: Paralelismo Monte Carlo con ProcessPoolExecutor
│   ├── theory.py                    # Oráculo analítico de colas M/M/1 y M/M/c (Erlang C)
│   └── workload.py                  # Generación de llegadas y servicios con semillas derivadas
└── tests/
    ├── test_step0.py                # Tests parametrizados para todos los escalones vs teoría y baseline
    ├── test_step5.py                # Tests de consistencia serial vs paralela en réplicas
    ├── test_theory.py               # Validación de fórmulas M/M/1 y M/M/c
    └── test_workload.py             # Verificación de reproducibilidad estocástica
```

---

## 6. Guía Rápida de Comandos Disponibles

```bash
# Sincronizar dependencias bloqueadas
uv sync

# Ejecutar suite de pruebas analíticas (74 passed)
uv run pytest -q

# Validar linter y estilo
uv run ruff check .

# Ejecutar el benchmark de humo de CI
uv run python -m scripts.smoke_benchmark

# Ejecutar la pipeline TODO-EN-UNO (Tests + Benchmarks + Figuras + Reportes + Dashboard Web)
uv run python -m scripts.run_all --mode quick --serve

# Servir el Dashboard Web directamente en el navegador
uv run python -m scripts.serve_dashboard
```
