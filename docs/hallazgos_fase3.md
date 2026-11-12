# Hallazgos Experimentales - Fase 3 (Escalones 4 y 5)

> Fecha de medición: 2026-11-12  
> Entorno de prueba: Windows 10, Intel(R) Core(TM) i5-10500T CPU @ 2.30GHz (6 núcleos físicos, 12 núcleos lógicos), 7.76 GB RAM, Python 3.12.13, NumPy 2.5.4, Numba 0.68.1.

---

## 1. Escalón 4: Compilación JIT con Numba (`step4_numba.py`)

### 1.1 Medición del Warm-up (Compilación JIT desacoplada)
Siguiendo la directiva de no mezclar el tiempo de compilación con la medición de simulación:
- **Tiempo de compilación en frío (*cold compilation / warmup*):** `0.2359 s`
- **Tiempo de ejecución en régimen (*warm run*, $n=100\,000, c=2$):** `0.0010 s` ($1.00\text{ ms}$)

La función `warmup()` dispara la compilación para las firmas esperadas antes de que comience el cronómetro del benchmark. Con `@njit(cache=True)`, las subsecuentes ejecuciones evitan la recompilación completa si los archivos de caché en `__pycache__` se mantienen válidos.

### 1.2 Comparación de la Escalera (Escalones 0 a 4)
Configuración de prueba: $n = 100\,000$ solicitudes, $c = 2$ servidores, $\lambda = 1.4, \mu = 1.0$ ($\rho = 0.70$), 3 repeticiones (mediana reportada).

| Escalón | Implementación | Tiempo mediana ($ms$) | Speedup vs. Baseline | Speedup vs. Escalón anterior |
|---|---|---|---|---|
| **0** | Baseline ingenuo (`step0_naive.py`) | $134.13\text{ ms}$ | $1.00\times$ | — |
| **1** | Estructuras de datos (`step1_datastructs.py`) | $102.88\text{ ms}$ | $1.30\times$ | $1.30\times$ |
| **2** | Python idiomático (`step2_idiomatic.py`) | $28.49\text{ ms}$ | $4.71\times$ | $3.61\times$ |
| **3** | NumPy (`step3_numpy.py`) | $28.39\text{ ms}$ | $4.72\times$ | $1.00\times$ |
| **4** | Numba JIT (`step4_numba.py`) | **$1.00\text{ ms}$** | **$133.97\times$** | **$28.39\times$** |

### 1.3 Análisis del Salto de Rendimiento en Numba
1. **El límite de NumPy superado:** Como se documentó en D17, la recurrencia con $c > 1$ servidores no es vectorizable mediante operaciones acumulativas simples (`scan`), lo que obligaba a NumPy a recurrir al bucle en Python (sin ganancia respecto al escalón 2).
2. **Eliminación de la sobrecarga del runtime de Python:** Numba compila el bucle secuencial a código de máquina nativo con LLVM. Los accesos al array `free_at` y el cálculo de `argmin` se realizan en registros y caché L1 sin boxing de objetos ni despachos dinámicos.
3. **Ganancia neta:** Una reducción de más de dos órdenes de magnitud ($134\times$) respecto al baseline, siendo el escalón de mayor aceleración secuencial de toda la escalera.

---

## 2. Escalón 5: Paralelismo Monte Carlo (`step5_parallel.py`)

### 2.1 Metodología
- El paralelismo se aplica a nivel de **réplicas Monte Carlo independientes**, donde cada réplica recibe una semilla derivada mediante `SeedSequence.spawn()` (D7).
- La base de comparación para el speedup paralelo es la **misma cantidad de réplicas en serie ejecutadas con el escalón 4** ($T_{\text{serie}}$).

### 2.2 Trampas detectadas: Arranque de procesos e IPC en Windows
Durante la experimentación se identificaron dos fenómenos críticos de ingeniería:
1. **Sobrecarga de `spawn` en Windows:** A diferencia del `fork` en Linux, Windows crea cada proceso de trabajo desde cero, cargando el ejecutable `python.exe` e importando los módulos. Lanzar un pool de 16 procesos toma entre 2 y 3 segundos. Si las tareas individuales son cortas ($< 0.1\text{ s}$), el costo de creación del pool supera ampliamente el tiempo de cómputo (speedup $< 0.2\times$).
2. **Sobrecarga de serialización IPC (Pickle):** Retornar arrays crudos de espera de $2\cdot 10^6$ elementos (`float64`, $\approx 16\text{ MB}$ por réplica) por pipes interproceso introduce cuellos de botella severos. Se implementó el parámetro `return_metrics=True` para computar métricas en el worker y transmitir únicamente el diccionario estadístico ligero.

### 2.3 Resultados de Escalamiento en Estado Estacionario
Configuración: $R = 24$ réplicas, $n = 2\cdot 10^6$ solicitudes por réplica, $c = 8$ servidores, $\rho = 0.75$, pool precalentado y cálculo de métricas local.
- **Tiempo serial (Escalón 4):** $T_{\text{serie}} = 3.0828\text{ s}$

| Procesos ($p$) | Tiempo medido ($s$) | Speedup ($S = T_{\text{serie}} / T_p$) | Eficiencia ($E = S / p$) |
|:---:|:---:|:---:|:---:|
| **1** | $2.8837\text{ s}$ | $1.07\times$ | $106.9\%$ |
| **2** | $1.6994\text{ s}$ | $1.81\times$ | $90.7\%$ |
| **4** | $1.3065\text{ s}$ | $2.36\times$ | $59.0\%$ |
| **6** | $1.3149\text{ s}$ | $2.34\times$ | $39.1\%$ |
| **8** | $1.2340\text{ s}$ | **$2.50\times$** | $31.2\%$ |
| **12 ($N$ lógicos)** | $1.4896\text{ s}$ | $2.07\times$ | $17.2\%$ |

### 2.4 Análisis del Comportamiento según la Ley de Amdahl y Topología de CPU
1. **Escalabilidad cuasi-lineal inicial:** Con 2 procesos se alcanza un speedup de $1.81\times$ y una eficiencia del $90.7\%$.
2. **Meseta de núcleos físicos:** La CPU i5-10500T cuenta con 6 núcleos físicos (12 lógicos vía Hyper-Threading). El speedup máximo alcanzado se estabiliza alrededor de **$2.50\times$** entre 6 y 8 trabajadores.
3. **Contención en Hyper-Threading:** Al elevar la concurrencia a 12 procesos (núcleos lógicos completos), el tiempo total empeora a $1.4896\text{ s}$ (speedup cae a $2.07\times$). Dado que las tareas son intensivas en cómputo numérico y ancho de banda de memoria L3/RAM, dos hilos lógicos en el mismo núcleo físico compiten por las mismas unidades de ejecución, introduciendo contención sin ganancia adicional.
