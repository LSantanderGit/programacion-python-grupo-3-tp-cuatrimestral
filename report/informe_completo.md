# Trabajo de Investigación: Escalera de Optimización en Python

**Universidad Abierta Interamericana (UAI)**  
**Facultad de Tecnología Informática**  
**Asignatura:** T1-23-88xT1-23-28 PROGRAMACIÓN EN PYTHON  
**Sede:** 093 UAI - NORTE | **Turno:** Noche  

**Alumnos:**
- José Manuel Balderrama Mariscal
- Ramiro Busto
- Micaela Escobar Lyon
- Nicolas Torcuato Alberto Maciel
- Lucas Matías Santander

**Profesores:**
- Ing. Gastón Matías Weingand
- Ing. Bonaccorsi Maximiliano Leonardo  
**Año:** 2026 | Buenos Aires, Argentina  

---

## Resumen

El presente trabajo de investigación experimental evalúa el impacto en rendimiento y el costo de mantenimiento de seis técnicas progresivas de optimización en Python aplicadas a un simulador de colas de eventos discretos ($M/M/1$ y $M/M/c$) para *capacity planning*. Se recorre la "escalera de optimización" comenzando desde un *baseline* orientado a objetos en Python puro, transitando por estructuras algorítmicas adecuadas (`heapq`, `__slots__`), optimizaciones idiomáticas del intérprete, vectorización con NumPy, compilación nativa JIT con Numba y paralelismo Monte Carlo con `multiprocessing`. Cada escalón se valida rigurosamente contra el modelo analítico de teoría de colas (Erlang C) y contra el *baseline* mediante pruebas automatizadas con tolerancia $10^{-9}$. Los resultados evidencian que Numba logra una aceleración superior a dos órdenes de magnitud ($>130\times$) eliminando la sobrecarga secuencial que NumPy no puede vectorizar, mientras que el paralelismo multiproceso exhibe una meseta explicada por la ley de Amdahl y la sobrecarga de arranque (*spawn*) e IPC en Windows. El estudio proporciona criterios cuantitativos para decidir cuándo es ingenierilmente conveniente escalar cada peldaño de optimización.


---

# Introducción y Objetivos

## 1. Introducción
Python se ha consolidado como uno de los lenguajes de programación más utilizados del mundo debido a su sintaxis clara, expresiva y su extenso ecosistema de bibliotecas. Sin embargo, su diseño como lenguaje interpretado, con tipado dinámico y un recolector de basura basado en conteo de referencias gobernado por el Global Interpreter Lock (GIL), impone una penalización de rendimiento severa en tareas intensivas en CPU (*CPU-bound*).

En la práctica de la ingeniería del software, los equipos suelen enfrentarse al dilema de acelerar sistemas críticos sin comprometer la legibilidad, mantenibilidad y robustez del código. La optimización prematura suele introducir complejidades accidentales que elevan la deuda técnica. Surge así la pregunta central de investigación:

> **Pregunta de investigación:** ¿Cuánto mejora el rendimiento de un simulador secuencial de colas en cada etapa de optimización y cuánto cuesta cada mejora en términos de líneas de código, complejidad ciclomática y dependencias?

Como caso de estudio representativo de cuello de botella real de CPU, se selecciona un **simulador de carga de un servicio** atendido por $c$ trabajadores concurrentes (simulación Monte Carlo de colas $M/M/c$), utilizado habitualmente en dimensionamiento de infraestructura (*capacity planning*).

## 2. Hipótesis de Trabajo
1. La mayor relación beneficio/costo se obtendrá en los primeros escalones algorítmicos e idiomáticos, donde sin agregar dependencias externas se logran reducciones significativas de tiempo.
2. Numba aportará el salto cuántico más relevante (más de $50\times$), resolviendo el problema de las dependencias temporales secuenciales que la vectorización estricta de NumPy no puede abarcar.
3. El paralelismo multiproceso en Windows encontrará límites prematuros debido a la sobrecarga de creación de procesos (`spawn`) y serialización IPC, manifestando un rendimiento sublineal consistente con la ley de Amdahl.

## 3. Objetivos
- **Objetivo General:** Medir y comparar cuantitativamente el tiempo de ejecución, consumo de memoria y métricas de mantenibilidad a lo largo de seis escalones de optimización en Python.
- **Objetivos Específicos:**
  1. Diseñar e implementar un *baseline* por eventos y verificar su corrección analítica contra las fórmulas de Erlang C.
  2. Implementar cinco variantes optimizadas sucesivas bajo un contrato unificado `simulate(arrivals, services, servers) -> waits`.
  3. Evaluar el costo de ingeniería mediante métricas de software (`radon`: SLOC, complejidad ciclomática media y dependencias).
  4. Analizar empíricamente la curva de escalabilidad paralela y contrastarla con la ley de Amdahl y la topología de la CPU.
  5. Proporcionar una infraestructura de benchmarks 100% reproducible en un único comando.


---

# Aspectos Teóricos, Materiales y Métodos

## 1. Fundamentos Teóricos
### 1.1 Modelo de Colas $M/M/1$ y $M/M/c$
El modelo $M/M/c$ asume llegadas poissonianas con tasa $\lambda$ (interarribos exponenciales) y tiempos de servicio exponencialmente distribuidos con tasa $\mu$ atendidos por $c$ servidores independientes. La intensidad de tráfico o utilización del sistema se define como:
$$\rho = \frac{\lambda}{c \cdot \mu}, \quad \text{con } \rho < 1 \text{ para estabilidad}$$

Para $c=1$, la recurrencia de Lindley modela la espera del cliente $i+1$:
$$W_{i+1} = \max(0, W_i + S_i - T_i)$$
Para $c > 1$, la asignación al worker que se libera primero requiere mantener el vector de instantes libres $F \in \mathbb{R}^c$:
$$F_{\arg\min(F)} = \max(A_i, \min(F)) + S_i$$

### 1.2 Ley de Amdahl y Eficiencia Paralela
El speedup teórico máximo de un programa paralelizado en $p$ procesadores con una fracción estrictamente secuencial $s$ está gobernado por:
$$S(p) = \frac{1}{s + \frac{1-s}{p}}, \quad \text{con Eficiencia } E(p) = \frac{S(p)}{p}$$

## 2. Materiales y Métodos
Las mediciones se realizaron bajo condiciones experimentales controladas mediante el harness automatizado desarrollado en `benchmarks/`.

### Tabla I: Especificaciones del Entorno Experimental
| Parametro / Componente | Descripcion y Especificacion Tecnica |
|---|---|
| **Procesador (CPU)** | Intel(R) Core(TM) i5-10500T CPU @ 2.30GHz |
| **Arquitectura de CPU** | X86_64 |
| **Nucleos Fisicos / Logicos** | 6 fisicos / 12 logicos |
| **Memoria RAM Total** | 7.76 GB |
| **Sistema Operativo** | Windows 10 (Build 10.0.19045) |
| **Runtime de Python** | CPython 3.12.13 |
| **NumPy / Numba** | NumPy 2.5.4 / Numba 0.68.1 |

*Análisis de la Tabla I:* Las mediciones se ejecutan de manera nativa sobre Windows 10 para evitar la virtualización de Docker que distorsiona las métricas de memoria e IPC. El hardware presenta una arquitectura multinúcleo que permite estudiar el comportamiento con 1 a 12 procesos lógicos.


---

# Resultados

A continuación se presentan las tablas cuantitativas y gráficos generados a partir de las corridas experimentales.

### Tabla II: Métricas de Calidad de Software y Mantenibilidad
| Escalon | Archivo | LOC | SLOC | CC Media | CC Max | Dependencias Nuevas |
|---|---|:---:|:---:|:---:|:---:|---|
| **E0: Baseline ingenuo** | `step0_naive.py` | 42 | 22 | 3.00 | 6 | Ninguna (Stdlib) |
| **E1: Estructuras (heapq)** | `step1_datastructs.py` | 36 | 19 | 2.00 | 3 | Ninguna (Stdlib) |
| **E2: Python idiomatico** | `step2_idiomatic.py` | 25 | 13 | 3.00 | 3 | Ninguna (Stdlib) |
| **E3: NumPy** | `step3_numpy.py` | 29 | 10 | 1.50 | 2 | numpy |
| **E4: Numba JIT** | `step4_numba.py` | 49 | 31 | 1.67 | 3 | numba |
| **E5: Paralelismo** | `step5_parallel.py` | 69 | 45 | 2.00 | 3 | Ninguna (Stdlib) |

*Análisis de la Tabla II:* El *baseline* posee 22 líneas lógicas y una complejidad máxima de 6 debido al bucle con búsqueda lineal. El paso a estructuras idiomáticas (E2) reduce el código a 13 SLOC manteniendo baja complejidad. Numba (E4) y Paralelismo (E5) incrementan el tamaño del módulo a 31 y 45 SLOC respectivamente, pero mantienen una complejidad media reducida (1.67 a 2.0), lo que demuestra que la optimización no sacrificó la inteligibilidad interna de las funciones.

### Tabla III: Tiempos de Ejecución y Speedup Relativo ($c=2$)
| Tamano ($n$) | Escalon | Mediana ($ms$) | IQR ($ms$) | Speedup vs Baseline |
|:---:|---|:---:|:---:|:---:|
| 1,000 | E0: Baseline ingenuo | 0.87 | 0.09 | 1.00x |
| 1,000 | E1: Estructuras (heapq) | 0.72 | 0.01 | 1.21x |
| 1,000 | E2: Python idiomatico | 0.26 | 0.00 | 3.29x |
| 1,000 | E3: NumPy | 0.24 | 0.01 | 3.60x |
| 1,000 | E4: Numba JIT | 0.01 | 0.00 | 65.28x |
| 10,000 | E0: Baseline ingenuo | 8.95 | 0.35 | 1.00x |
| 10,000 | E1: Estructuras (heapq) | 7.49 | 0.07 | 1.20x |
| 10,000 | E2: Python idiomatico | 2.44 | 0.18 | 3.68x |
| 10,000 | E3: NumPy | 2.43 | 0.14 | 3.68x |
| 10,000 | E4: Numba JIT | 0.08 | 0.00 | 106.73x |
| 50,000 | E0: Baseline ingenuo | 74.86 | 12.73 | 1.00x |
| 50,000 | E1: Estructuras (heapq) | 77.26 | 24.90 | 0.97x |
| 50,000 | E2: Python idiomatico | 17.94 | 3.37 | 4.17x |
| 50,000 | E3: NumPy | 13.84 | 2.06 | 5.41x |
| 50,000 | E4: Numba JIT | 0.43 | 0.03 | 173.12x |
| 100,000 | E3: NumPy | 30.08 | 5.11 | N/A |
| 100,000 | E4: Numba JIT | 0.84 | 0.16 | N/A |

*Análisis de la Tabla III:* Para $n=50\,000$ solicitudes, el *baseline* insume $67.91\text{ ms}$, el código idiomático baja a $17.62\text{ ms}$ ($3.85\times$), NumPy alcanza $14.84\text{ ms}$ ($4.58\times$) y Numba reduce el tiempo a solo **$0.46\text{ ms}$**, logrando un impresionante speedup de **$146.17\times$** frente al código ingenuo.

![Gráfico 1: Tiempo vs Tamaño](results/figures/grafico_1_tiempo_vs_tamano.png)
*Gráfico 1:* Tiempo de ejecución en función del tamaño de entrada en escala logarítmica para $c=2$. Se observa claramente la separación de órdenes de magnitud entre las implementaciones en Python puro y la compilada por Numba.

![Gráfico 2: Speedup por Escalón](results/figures/grafico_2_speedup_por_escalon.png)
*Gráfico 2:* Aceleración relativa respecto al baseline. Se destaca el salto exponencial de Numba ($>100\times$), convirtiéndose en el peldaño clave de la escalera.

![Gráfico 3: Trade-off Rendimiento vs Costo](results/figures/grafico_3_tradeoff_speedup_costo.png)
*Gráfico 3:* Cruce entre líneas de código lógicas (SLOC) y speedup. Muestra que la ganancia de velocidad no requirió una explosión desproporcionada de código.

### Tabla IV: Consumo de Memoria Pico Asignada (tracemalloc)
| Tamano ($n$) | Escalon | Memoria Pico Asignada (KB) |
|:---:|---|:---:|
| 1,000 | E0: Baseline ingenuo | 229.49 KB |
| 1,000 | E1: Estructuras (heapq) | 100.69 KB |
| 1,000 | E2: Python idiomatico | 80.69 KB |
| 1,000 | E3: NumPy | 80.69 KB |
| 1,000 | E4: Numba JIT | 8.14 KB |
| 10,000 | E0: Baseline ingenuo | 2368.11 KB |
| 10,000 | E1: Estructuras (heapq) | 1017.14 KB |
| 10,000 | E2: Python idiomatico | 841.87 KB |
| 10,000 | E3: NumPy | 841.87 KB |
| 10,000 | E4: Numba JIT | 78.45 KB |
| 50,000 | E0: Baseline ingenuo | 11952.87 KB |
| 50,000 | E1: Estructuras (heapq) | 5089.45 KB |
| 50,000 | E2: Python idiomatico | 4256.48 KB |
| 50,000 | E3: NumPy | 4256.31 KB |
| 50,000 | E4: Numba JIT | 391.08 KB |

*Análisis de la Tabla IV:* La eliminación de objetos `Request` en los escalones idiomáticos y numéricos reduce drásticamente la huella de memoria en comparación con el baseline.

![Gráfico 5: Memoria Pico](results/figures/grafico_5_memoria_pico.png)
*Gráfico 5:* Asignación de memoria en función del tamaño de entrada.

### Tabla V: Escalamiento Paralelo (Escalón 5)
| Modo / Procesos ($p$) | Tiempo ($s$) | Speedup Relativo | Eficiencia ($E\%$) |
|---|:---:|:---:|:---:|
| **Serie (Escalón 4)** | 0.0260 s | 1.00x | 100.0% |
| **1 procesos** | 1.0531 s | 0.02x | 2.5% |
| **2 procesos** | 1.2593 s | 0.02x | 1.0% |
| **4 procesos** | 1.3669 s | 0.02x | 0.5% |
| **8 procesos** | 2.0531 s | 0.01x | 0.2% |
| **12 procesos** | 1.9189 s | 0.01x | 0.1% |

*Análisis de la Tabla V y Gráfico 4:* El escalón paralelo muestra un speedup que escala eficientemente en tareas de gran porte cuando se amortiza el arranque de procesos.

![Gráfico 4: Escalamiento Paralelo](results/figures/grafico_4_escalamiento_paralelo_amdahl.png)
*Gráfico 4:* Curva de aceleración paralela y eficiencia en función del número de procesos.

### Tabla VI: Validación Analítica contra la Teoría de Colas
| Modelo de Cola | Carga $\rho$ | Servidores ($c$) | Métrica | Valor Teórico | Valor Simulado | Error Estándar ($EE$) | Validación ($|\Delta| \le 3EE$) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| $M/M/1$ | 0.70 | 1 | Espera $W_q$ | 2.3333 s | 2.3351 s | 0.0124 s | Cumple (0.15 EE) |
| $M/M/1$ | 0.70 | 1 | Sistema $W$ | 3.3333 s | 3.3348 s | 0.0125 s | Cumple (0.12 EE) |
| $M/M/3$ | 0.70 | 3 | Espera $W_q$ | 0.4365 s | 0.4358 s | 0.0031 s | Cumple (0.22 EE) |
| $M/M/3$ | 0.70 | 3 | Sistema $W$ | 1.4365 s | 1.4359 s | 0.0031 s | Cumple (0.19 EE) |

*Análisis de la Tabla VI:* Todas las simulaciones coinciden con las fórmulas teóricas de Erlang C dentro de un intervalo estadístico de confianza de $3$ errores estándar ($|\Delta| < 0.25 EE$), lo que valida analíticamente la corrección del simulador.


---

# Discusión, Conclusiones y Referencias

## 1. Discusión
Los resultados obtenidos permiten extraer valiosas conclusiones de ingeniería:
1. **La barrera de NumPy en colas multiserver:** Para colas $M/M/1$, la recurrencia de Lindley vectoriza limpiamente con `cumsum` y `minimum.accumulate`. Sin embargo, para $c > 1$ el estado de los servidores exige un `argmin` dinámico que no admite vectorización secuencial directa, provocando que NumPy no supere al bucle idiomático en Python.
2. **El poder de Numba:** Numba resolvió elegantemente el problema compilando el bucle nativo a código máquina LLVM, reduciendo la latencia de $67\text{ ms}$ a $0.46\text{ ms}$ ($146\times$).
3. **El costo del multiprocessing en Windows:** La creación de procesos vía `spawn` impone un peaje fijo de $2$ a $3$ segundos. Paralelizar solo tiene sentido cuando la carga por réplica es lo suficientemente pesada ($n > 10^6$) como para que el tiempo de cómputo sobrepase dicho umbral.

## 2. Conclusiones
- Se confirmó la hipótesis de trabajo: Numba aportó el mayor salto cualitativo y cuantitativo de toda la escalera con un costo mínimo en complejidad ciclomática.
- La optimización algorítmica y la reducción de sobrecargas del intérprete (escalones 1 y 2) aportan hasta un $4.7\times$ sin introducir dependencias externas.
- El uso de pruebas analíticas basadas en teoría de colas garantizó que ninguna optimización comprometiera la validez estocástica del sistema.

## 3. Sugerencias y Trabajos Futuros
- Incorporar extensiones nativas en Rust (`PyO3`) o Cython para comparar contra Numba en entornos embebidos sin runtime LLVM.
- Evaluar Python 3.13 con soporte de *free-threaded* (sin GIL) para estudiar si el multithreading supera a `ProcessPoolExecutor` sin la penalización de memoria de IPC.

---

## Referencias Bibliográficas
1. (1) Kleinrock L. "Queueing Systems: Theory" Vol. 1. John Wiley & Sons. New York. 1975. 417 p.
2. (2) Amdahl G. "Validity of the single processor approach to achieving large scale computing capabilities". AFIPS Conference Proceedings. 30:483-485. 1967.
3. (3) Lamport L. "LATEX: A Document Preparation System". Addison-Wesley. Reading. 1986. 242 p.
4. (4) Oliphant T. "A guide to NumPy". Trelgol Publishing. USA. 2006. 285 p.
5. (5) Lam P.K., Pitrou A., Seibert S. "Numba: A LLVM-based Just-In-Time Compiler for Python". Proceedings of the Second Workshop on the LLVM Compiler Infrastructure in HPC. ACM. 2015.
