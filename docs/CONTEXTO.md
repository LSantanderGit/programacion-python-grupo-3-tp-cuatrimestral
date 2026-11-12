Contexto del proyecto: "Escalera de optimización"

Documento de contexto para el equipo y para cualquier agente de IA que trabaje en el proyecto. Resume qué se decidió, por qué, qué debe contener el proyecto y qué sigue abierto. Última actualización: 2026-11-06. Repositorio (ya existe): https://github.com/LSantanderGit/programacion-python-grupo-3-tp-cuatrimestral. Entrega: 19/11/2026.

1. Resumen en 30 segundos
Qué es: trabajo de investigación grupal de la asignatura T1-23-88xT1-23-28 PROGRAMACIÓN EN PYTHON (Facultad de Tecnología Informática, Universidad Abierta Interamericana, UAI - Sede: 093 UAI - NORTE, Turno Noche, Grupo 3); profesores: Ing. Gastón Matías Weingand e Ing. Bonaccorsi Maximiliano Leonardo. Estudia cómo se acelera un programa en Python etapa por etapa (la "escalera de optimización") y cuánto cuesta cada mejora en legibilidad y mantenibilidad.
Tema elegido: Rendimiento (área sugerida en la consigna).
Caso de estudio: un simulador de carga de un servicio (cola de requests atendida por N workers, simulación Monte Carlo) para estimar utilización y latencia (p95) antes de que el servicio se sature.
Validación: cada versión debe dar el mismo resultado que el baseline y coincidir con la teoría de colas (M/M/1 y M/M/c).
Entregables: repositorio reproducible en Python (código, tests, benchmarks, scripts), informe de investigación y una presentación de 4 a 5 diapositivas de contenido (más carátula y cierre).
Resultado central esperado: una tabla de speedup contra costo por escalón, con la discusión de cuándo conviene subir cada peldaño.
2. La consigna (restricciones que mandan)
Grupo de 2 a 4 integrantes.
Presentación del trabajo en la clase 15, con sugerencias y correcciones para la entrega final en la clase 16. Las dudas se consultan con el tutor (docente).
Temática relacionada con la asignatura, dentro del contexto de la ingeniería del software.
Áreas sugeridas: paradigmas de software, rendimiento, codificación, calidad del producto, procesamiento concurrente/paralelo, comunicaciones, chatbots, IoT, robótica, aprendizaje automático, redes neuronales, data science, algoritmos evolutivos, u otra acordada con el tutor.
Toda la codificación, pruebas conceptuales y desarrollos deben hacerse en Python, con las buenas prácticas y herramientas vistas durante la cursada y en materias previas.
3. Historial de decisiones (cómo se llegó a la forma final)
#	Decisión	Estado	Razonamiento
1	Se revisaron todas las áreas sugeridas con su dificultad y un proyecto posible en Python.	Hecho	Punto de partida para elegir con criterio.
2	El equipo se había inclinado primero por Redes Neuronales.	Descartado	Riesgo de que el trabajo se vuelva de ML y no de ingeniería del software, de perderse ajustando hiperparámetros y de caer en ejemplos repetidos (MNIST, perros y gatos).
3	Se evaluaron Chatbots y Comunicaciones como alternativas.	Descartado	Se analizaron enfoques, riesgos y alcance; el equipo prefirió otra dirección.
4	Se eligió Rendimiento.	Decidido	Resultados medibles y objetivos, conecta con ingeniería del software (trade-offs, calidad, CI) e integra varias áreas (codificación, calidad, paralelismo).
5	Se adoptó el enfoque de la "escalera de optimización" (proyecto A de la propuesta de Rendimiento).	Decidido	Al equipo le gustó la idea; permite medir cada técnica por separado y comparar costo contra beneficio. Se complementa con regresión de rendimiento en CI.
6	Se evaluaron cinco sistemas candidatos para aplicar la escalera: simulador de carga/colas (A), motor de análisis de logs (B), deduplicador difuso de catálogo (C), procesamiento de imágenes en lote (D) y clásicos como Mandelbrot o n-cuerpos (E).	Hecho	Criterios: cuello de botella real de CPU, que cada escalón aplique de forma natural, oráculo de corrección, tamaño de entrada escalable, que sea un "sistema" y alcance acotado.
7	Se eligió la opción A: simulador de carga de un servicio.	Decidido	Tiene propósito real (capacity planning), oráculo analítico (fórmulas M/M/1 y M/M/c), todos los escalones aplican de forma honesta y las réplicas Monte Carlo son independientes (sirve para analizar Amdahl). La opción B (logs) quedó solo como segundo caso posible si sobra tiempo; no está decidida.
8	La replicabilidad se diseñó para una sola PC y para que cualquiera pueda repetir el experimento.	Decidido	Los tiempos absolutos no se replican entre máquinas; lo replicable son entorno, resultados numéricos y conclusiones relativas (speedup, forma de las curvas). Ver sección 6.
9	Se preparó la presentación inicial (carátula + 5 diapositivas + cierre) y un documento con la estructura de cada diapositiva.	Hecho	Contenido: tema, por qué lo eligieron, aplicación, escalones con justificación, metodología.
10	Informe en Google Docs; código en el repo de GitHub del grupo; mediciones finales en una PC con Windows 10, Intel Core i9 de 13.ª generación y 32 GB de RAM DDR5.	Decidido	Definido por el grupo el 2026-11-06. La entrega es el 19/11/2026.
4. Qué debe tener el proyecto
4.1 Funcionalidad del simulador
Simula un servicio con N workers y una cola de requests: llegadas aleatorias, tiempos de servicio aleatorios, atención en orden de llegada.
Calcula por corrida: utilización, tiempo medio de espera en cola, tiempo medio en el sistema y percentiles de latencia (p95, y opcionalmente p99).
Soporta muchas réplicas independientes (Monte Carlo) para obtener resultados estables.
Tamaños de entrada escalables: de 10³ a 10⁷ requests, más servidores y más réplicas.
4.2 Los escalones de la escalera

Todos los escalones implementan la misma interfaz y reciben las mismas entradas.

Escalón	Técnica	Qué ataca	Notas para la implementación
0	Baseline ingenuo: Python puro, cada request es un objeto, cola como lista, bucle for que avanza el reloj.	Nada: es la referencia.	Sin pensar en rendimiento. Debe validarse contra la teoría antes de seguir.
1	Estructuras de datos y algoritmo: collections.deque, heapq, __slots__.	Complejidad algorítmica (por ejemplo list.pop(0) es O(n)).	Suele dar el mayor salto con el menor costo. Mensaje: "antes de compilar, mejorar el algoritmo".
2	Python idiomático: variables locales en el bucle caliente, generadores, menos llamadas intermedias.	Overhead del intérprete.	Ganancia moderada; muestra el costo en legibilidad.
3	NumPy: generar llegadas y servicios en bloque, np.cumsum, etc.	Bucles en Python puro.	La recurrencia de Lindley W[i+1] = max(0, W[i] + S[i] - A[i+1]) es secuencial y no se vectoriza de forma directa. Documentar esto como hallazgo (hay trucos con np.maximum.accumulate).
4	Numba (@njit) sobre el bucle secuencial.	Lo que NumPy no pudo resolver.	Mayor salto esperado (10x a 100x). Medir aparte el warm-up de compilación; usar cache=True.
5	Paralelismo: réplicas Monte Carlo con multiprocessing o concurrent.futures.	Uso de varios núcleos.	Medir speedup y eficiencia (speedup = T_base / T_opt, eficiencia = speedup / n_procesos) con 1, 2, 4, ... hasta los núcleos lógicos; contrastar con la ley de Amdahl. Con Numba también se puede probar prange.
6 (opcional)	Extensión nativa: Cython, C con ctypes o Rust con PyO3.	Límite de Python.	Solo si sobra tiempo y nunca como requisito del camino principal (requiere compilador).

Transversal: pytest-benchmark en el pipeline de CI para fallar si un cambio empeora los tiempos más allá de un umbral (regresión de rendimiento).

4.3 Oráculo de corrección (teoría de colas)

Para una cola M/M/1 con tasa de llegada λ y tasa de servicio μ (válido con λ < μ):

Utilización: ρ = λ / μ
Tiempo medio de espera en cola: Wq = ρ / (μ - λ)
Tiempo medio en el sistema: W = 1 / (μ - λ)

Para varios workers se usa M/M/c (fórmula de Erlang C). Estas fórmulas viven en theory.py y los tests comparan cada escalón contra ellas y contra el baseline.

4.4 Qué se mide en cada escalón
Tiempo (mediana y rango intercuartil de varias corridas) y speedup contra el baseline y contra el escalón anterior.
Memoria (tracemalloc, o scalene).
Escalabilidad: tiempo contra tamaño de entrada (10³ a 10⁷).
Corrección: error contra la solución teórica y contra el baseline con la misma semilla.
Costo de mantenimiento: líneas de código, complejidad ciclomática (radon), dependencias nuevas y una nota cualitativa de legibilidad.
5. Decisiones técnicas para el desarrollo en Python
Python 3.12 (o la versión que se acuerde y se fije), con dependencias bloqueadas con uv (pyproject.toml + uv.lock). Alternativa: requirements.txt con versiones exactas (NumPy y Numba deben fijarse juntas).
Una interfaz común para todos los escalones, por ejemplo simulate(arrivals, services, servers) -> resultados, para que el harness, los benchmarks y los tests parametrizados los traten por igual.
Entradas compartidas y reproducibles: los tiempos de llegada y de servicio se generan una sola vez con np.random.default_rng(seed) y se pasan a todas las implementaciones. Si cada versión usara su propio generador, los resultados exactos no serían comparables. En el escalón paralelo, cada réplica recibe una semilla derivada con SeedSequence.spawn().
Separar la generación de números aleatorios de la simulación, para poder medir cada parte por separado.
Calidad: tests con pytest (cada escalón contra el baseline y contra la teoría), type hints, linter (ruff), radon para métricas, configuración por variables de entorno. Alinear la lista exacta de herramientas con lo visto en la cursada.
Sin dependencias difíciles en el camino principal: Cython o C/Rust son opcionales y están marcados como tales.
Portabilidad: debe funcionar en Windows, Linux y macOS. Por eso el punto de entrada es un script de Python (no make).
Estructura propuesta dentro del repo existente

El repo es programacion-python-grupo-3-tp-cuatrimestral (ya creado en GitHub, hoy solo con README.md). La estructura se arma en su raíz:

programacion-python-grupo-3-tp-cuatrimestral/
├── pyproject.toml          # dependencias y versión de Python
├── uv.lock                 # versiones bloqueadas
├── README.md               # "cómo replicar" en pocos pasos
├── CLAUDE.md               # reglas para agentes de IA
├── docs/
│   ├── CONTEXTO.md        # este documento
│   └── decisiones.md      # registro de decisiones técnicas
├── .github/workflows/ci.yml
├── src/queue_sim/          # paquete de Python del simulador
│   ├── workload.py         # generación de entradas (rng, semillas)
│   ├── metrics.py          # métricas comunes (media, p95, utilización)
│   ├── step0_naive.py
│   ├── step1_datastructs.py
│   ├── step2_idiomatic.py
│   ├── step3_numpy.py
│   ├── step4_numba.py
│   ├── step5_parallel.py
│   └── theory.py           # fórmulas M/M/1 y M/M/c (oráculo)
├── tests/                  # cada escalón vs baseline y vs teoría
├── benchmarks/
│   ├── harness.py          # warm-up, repeticiones, medición
│   ├── config.py           # matriz de tamaños por escalón
│   └── env_info.py         # captura automática del entorno
├── scripts/
│   ├── run_all.py          # único punto de entrada
│   └── make_report.py      # tablas y gráficos desde results/raw
├── report/                 # borradores por capítulo del informe
└── results/
    ├── raw/                # CSV/JSON crudos + env.json
    └── figures/
6. Metodología y replicabilidad (decidido)
Dos niveles de replicabilidad: el entorno y los resultados numéricos sí se garantizan; los tiempos absolutos no. Las conclusiones centrales se expresan en ratios de speedup y tendencias, y los segundos absolutos van como contexto junto con las especificaciones de la máquina.
Un solo punto de entrada compatible con todos los sistemas operativos:
python -m scripts.run_all --mode quick (tamaños chicos, pocas repeticiones, unos 2 a 3 minutos, para que cualquiera verifique).
python -m scripts.run_all --mode full (tamaños grandes y muchas repeticiones, alimenta el informe).
Ejecuta en orden: tests de corrección, benchmarks, generación de tablas y gráficos desde los datos crudos.
Medición rigurosa: time.perf_counter(), descarte del warm-up (JIT de Numba), entre 7 y 30 repeticiones, reporte de mediana y rango intercuartil (no mínimo ni promedio), varios tamaños de entrada, orden de las pruebas intercalado para mitigar el thermal throttling.
Registro automático del entorno en env.json (CPU, núcleos físicos y lógicos, RAM, sistema operativo, versiones de Python, NumPy y Numba) con cada corrida.
Datos crudos separados de los gráficos: los benchmarks escriben CSV/JSON en results/raw/; un script aparte regenera tablas y figuras sin volver a medir.
Reducir ruido en la PC: notebook enchufada, plan de energía en alto rendimiento, cerrar programas en segundo plano, misma máquina para todos los benchmarks finales.
Docker: se usa para tests y CI, no para las mediciones finales. En Windows y macOS Docker corre sobre una máquina virtual y distorsiona justo el multiprocessing y la memoria. Si igual se mide en Docker, debe documentarse como limitación.
Prueba final de replicabilidad: que un compañero clone el repo en otra PC y siga el README sin ayuda.
7. Errores a evitar
Optimizar partes que no son el cuello de botella (medir antes con un profiler).
Que una versión optimizada dé resultados distintos al baseline: la corrección va primero.
Comparar implementaciones que no hacen exactamente lo mismo o que usan distintas semillas.
Mezclar el costo de compilación JIT con las mediciones normales.
Paralelizar tareas chicas: el costo de crear procesos y serializar (pickle) puede superar la ganancia.
Medir un solo tamaño de entrada o en una sola máquina y generalizar; declarar esas limitaciones en el informe.
Quedarse solo en mostrar números sin explicar por qué ocurre cada diferencia.
Cubrir demasiado: es mejor una escalera completa y bien medida que dos a medias.
8. Estructura y formato del informe (según la guía oficial "Formato para presentación del trabajo de investigación")
8.1 Capítulos exigidos, en este orden
Carátula con: Universidad Abierta Interamericana, Facultad de Tecnología Informática, Sede 093 UAI - NORTE, "Asignatura: T1-23-88xT1-23-28 PROGRAMACIÓN EN PYTHON", título del trabajo, nombres de los alumnos, "Trabajo de investigación", profesores (Ing. Gastón Matías Weingand e Ing. Bonaccorsi Maximiliano Leonardo), Buenos Aires - Argentina y año.
Hoja en blanco.
Dedicatoria (opcional).
Agradecimientos.
Índice.
Introducción: origen del problema o tema, justificación del tema e importancia del problema; debe responder "¿por qué y para qué se realiza la investigación?".
Aspectos teóricos: fundamentos teóricos de los supuestos e hipótesis de trabajo, y antecedentes relevantes. Si el estudio es explicativo, se cierra con la hipótesis de trabajo.
Objetivos: enunciados concisos de en qué consiste la investigación.
Materiales y métodos: responde "¿cómo se realizó la investigación?"; universo y muestra, procedimiento y su justificación, instrumentos de medición y materiales.
Resultados: tablas y gráficos, con el análisis a continuación de cada uno.
Discusión: comparación con trabajos consultados, explicación de diferencias, resultados esperados e inesperados y dificultades.
Conclusiones: deben responder a la hipótesis y/o los objetivos.
Sugerencias: hasta dónde avanzó la investigación, nuevos aspectos que surgen y aportes para estudios similares.
Resumen: conciso, de hasta unas 250 palabras.
Referencias bibliográficas: lista numerada correlativamente; las citas en el texto van con el número entre paréntesis.
Anexos y apéndice.
8.2 Formato
Hoja tamaño carta; texto a doble espacio.
Márgenes: superior 4 cm, inferior 4 cm, izquierdo 4 cm, derecho 2,5 cm.
Numeración de páginas arriba a la derecha, desde la introducción.
Tablas numeradas con números romanos, correlativas y con título descriptivo. Gráficos numerados con números arábigos, correlativos. Fotografías e imágenes tituladas y numeradas.
Referencias bibliográficas: para libros, (n) Apellido I. "Título" Nº Ed. Editorial. Lugar. Año. Total de páginas, páginas citadas y capítulo; para revistas, (n) Autor. Título del artículo. "Revista abreviada" Vol.(Nº):páginas inicial-final. Mes año. Más de tres autores: el primero y "et al".
8.3 Cómo encajan las decisiones del proyecto en esos capítulos
Capítulo de la guía	Contenido del proyecto
Introducción	Por qué importa el rendimiento en Python y la pregunta de investigación; por qué se eligió el simulador de carga (capacity planning).
Aspectos teóricos	Complejidad algorítmica, CPU-bound vs I/O-bound, GIL, por qué Python es lento, vectorización y localidad de caché, ley de Amdahl, speedup y eficiencia, teoría de colas (M/M/1, M/M/c). Hipótesis de trabajo (a formular): por ejemplo, que la mayor parte de la ganancia aparece en los primeros escalones (algoritmo y estructuras de datos) y en Numba, mientras que el paralelismo rinde menos de lo ideal por la fracción secuencial y el costo de procesos.
Objetivos	Medir el speedup y el costo de mantenimiento de cada escalón; validar contra la teoría; dejar un experimento replicable.
Materiales y métodos	El "universo" son las implementaciones de los escalones y los tamaños de entrada (10³ a 10⁷); instrumentos: perf_counter, pytest-benchmark, tracemalloc, radon, env.json; procedimiento de la sección 6.
Resultados	Tablas (romanas) y gráficos (arábigos) de tiempo, speedup, memoria, escalabilidad, error contra la teoría y costo de mantenimiento, con el análisis debajo de cada uno.
Discusión	Por qué ocurre cada diferencia, hallazgos como la no vectorización de la recurrencia de Lindley, el costo del warm-up de Numba y el límite de Amdahl; dificultades y limitaciones (una sola máquina).
Conclusiones y sugerencias	Respuesta a la hipótesis; cuándo conviene cada técnica; estudios futuros (extensión nativa, segundo caso de estudio, otras máquinas).
Anexos	Repositorio, scripts y datos crudos.

El informe debe seguir esta estructura de la guía oficial; la estructura en seis partes usada en la propuesta inicial era solo una referencia y queda reemplazada.

9. Presentación inicial (ya preparada)
Formato: PowerPoint (importable a Google Slides), carátula + 5 diapositivas + cierre, con notas del orador.
Diapositivas: (1) el tema, (2) por qué lo elegimos, (3) dónde lo aplicamos, (4) la escalera de optimización, (5) cómo medimos y replicamos.
Motivos de elección propuestos: habilidad profesional, resultados objetivos, es ingeniería del software, integra varias áreas. Están pendientes de ajustar con las razones reales del grupo.
Existe además un documento con la estructura de cada diapositiva y el cumplimiento de la consigna.
10. Reparto de tareas sugerido (2 a 4 integrantes)
Frente	Responsabilidad
Baseline y tests	Escalón 0, theory.py, tests de corrección
Optimización algorítmica y NumPy	Escalones 1 a 3
Numba y paralelismo	Escalones 4 y 5, speedup y eficiencia
Benchmarks, CI e informe	Harness, env.json, pytest-benchmark, gráficos y redacción

Con menos integrantes, los frentes se combinan.

11. Pendientes y preguntas abiertas
 Completar los nombres de los integrantes (carátula y reparto de tareas).
 Validar con el tutor que el simulador de colas encaja como caso de estudio.
 Ajustar con el grupo los motivos de elección de la diapositiva 2.
 Elegir la PC de las mediciones finales: Windows 10, Intel Core i9 de 13.ª generación, 32 GB DDR5 (el modelo exacto de CPU lo registra env.json).
 Acordar los hitos internos hasta la entrega del 19/11/2026.
 Formular la hipótesis de trabajo definitiva (la sección 8.3 tiene una propuesta).
 Definir tutor principal y tutores asociados para la carátula del informe.
 Confirmar la versión de Python y las herramientas de calidad vistas en la cursada.
 Decidir si se incluye el escalón 6 (extensión nativa) y si hay un segundo caso de estudio (logs); por defecto, no.
 Crear la estructura base dentro del repo existente, con workload.py, el baseline y los tests contra M/M/1.
12. Notas para agentes de IA
Responder en español.
El proyecto es de ingeniería del software aplicada a rendimiento, no un ejercicio suelto de optimización: toda propuesta debe preservar la corrección, la reproducibilidad y el análisis del costo en mantenibilidad.
Respetar la interfaz común de los escalones y las entradas compartidas por semilla; no introducir generadores aleatorios propios en cada escalón.
No presentar tiempos absolutos como resultado general; priorizar speedup y tendencias, siempre con el entorno registrado.
Todo el código es Python; evitar dependencias que compliquen la instalación en el camino principal.
Lo marcado como Decidido en la sección 3 no debe reabrirse sin que el grupo lo pida; lo opcional y lo pendiente sí admite propuestas.
El repositorio ya existe (ver arriba); no crear otro ni renombrarlo.
