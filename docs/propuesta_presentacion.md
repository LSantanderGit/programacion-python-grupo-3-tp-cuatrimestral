# Escalera de optimización en Python: propuesta y estructura de la presentación
 
Oct 1, 2026
 
## Resumen de la propuesta
 
Vamos a estudiar cómo se acelera un programa en Python etapa por etapa, y cuánto cuesta cada mejora, usando un simulador de carga de un servicio como caso de estudio.
 
- **Tema:** Rendimiento (área sugerida en la consigna).
 
- **Pregunta de investigación:** ¿cuánto mejora el rendimiento de un simulador de colas en cada etapa de optimización (estructuras de datos, NumPy, Numba, paralelismo) y cuánto cuesta cada mejora en legibilidad y mantenibilidad?
 
- **Aplicación:** simulación Monte Carlo de un servicio con N workers y una cola de requests, para estimar utilización y latencia (p95) antes de que el servicio se sature.
 
- **Validación:** cada versión optimizada debe dar el mismo resultado que el baseline y coincidir con las fórmulas teóricas de colas M/M/1 y M/M/c.
 
- **Entregable:** repositorio reproducible en Python (tests, benchmarks, scripts), un informe y esta presentación.
 
## Estructura de la presentación
 
La presentación tiene una carátula, cinco diapositivas de contenido y un cierre; cada una responde una pregunta que el docente va a querer ver contestada.
 
| # | Diapositiva | Pregunta que responde | Contenido clave |
| --- | --- | --- | --- |
| 0 | Carátula | ¿De qué trata el trabajo? | Título, materia, integrantes, fecha |
| 1 | El tema: Rendimiento en Python | ¿Qué vamos a investigar? | Qué es el rendimiento, por qué Python necesita optimización, pregunta de investigación |
| 2 | Por qué lo elegimos | ¿Por qué nos resultó importante e interesante? | Cuatro motivos: habilidad profesional, resultados objetivos, ingeniería del software, integración de áreas |
| 3 | La aplicación: simulador de carga | ¿En qué sistema lo aplicamos? | Qué simula, para qué sirve (capacity planning), por qué es buen caso de estudio |
| 4 | La escalera de optimización | ¿Cómo lo dividimos y por qué en ese orden? | Escalones 0 a 5 con una línea de justificación cada uno |
| 5 | Cómo lo medimos y replicamos | ¿Cómo sabemos que los resultados son confiables? | Corrección contra teoría, medición rigurosa, un comando para replicar, entregables |
| 6 | Cierre | ¿Qué esperamos obtener? | Resultado esperado (tabla speedup vs costo), próximos pasos, preguntas |
 
Cada diapositiva lleva un visual (íconos, escalera, diagrama) y poco texto; el detalle va en las notas del orador del archivo .pptx y en este documento.
 
## Por qué elegimos Rendimiento
 
Elegimos Rendimiento porque convierte la optimización en algo medible y porque obliga a decidir cuándo vale la pena sacrificar legibilidad por velocidad. Estos son los motivos propuestos para la diapositiva 2; conviene ajustarlos con las razones reales del grupo.
 
- **Es una habilidad profesional concreta.** Python es de los lenguajes más usados, pero es lento por diseño (intérprete, tipado dinámico, GIL). Saber medir y elegir la técnica correcta es lo que separa un script que funciona de un sistema que escala.
 
- **Los resultados son objetivos.** Cada mejora se expresa en un número (speedup, memoria, error contra la teoría), no en una opinión.
 
- **Es ingeniería del software, no solo programación.** Aparecen los trade-offs reales: rendimiento contra mantenibilidad, el riesgo de la optimización prematura, la corrección antes que la velocidad y la detección de regresiones de rendimiento en CI.
 
- **Integra varias áreas de la lista.** En un solo trabajo se tocan codificación, calidad del producto y procesamiento concurrente y paralelo.
 
- **La escalera ordena el aprendizaje.** Ir de lo más barato a lo más costoso permite entender por qué cada técnica existe y cuándo conviene.
 
## La aplicación: simulador de carga de un servicio
 
Aplicamos la escalera a un simulador que responde una pregunta de capacity planning: cuántos requests por segundo aguanta un servicio con N workers antes de que la latencia p95 se dispare.
 
El simulador genera llegadas y tiempos de servicio aleatorios, los procesa con una cola de N servidores y calcula utilización, tiempo de espera y latencias. Se repite muchas veces (Monte Carlo) para obtener resultados estables.
 
Por qué es un buen caso de estudio:
 
- **Cuello de botella real de CPU:** un bucle secuencial con millones de eventos, donde optimizar tiene efecto visible.
 
- **Todos los escalones aplican de forma honesta**, cada uno con una razón distinta.
 
- **Tiene oráculo analítico:** para una cola M/M/1 con tasa de llegada λ y tasa de servicio μ, la teoría da resultados exactos contra los que validar cada versión.
 
- **Las réplicas son independientes**, lo que permite analizar speedup y eficiencia del paralelismo con la ley de Amdahl.
 
- **Escala fácil:** 10³ a 10⁷ requests, más servidores, más réplicas.
 
- **Es un sistema con propósito**, no un ejercicio suelto, lo que sostiene el enfoque de ingeniería del software.
 
Fórmulas de referencia para M/M/1 (válidas con λ < μ):
 
\rho = \frac{\lambda}{\mu}, \qquad W_q = \frac{\rho}{\mu - \lambda}, \qquad W = \frac{1}{\mu - \lambda}
 
Aquí ρ es la utilización del servidor, W_q el tiempo medio de espera en cola y W el tiempo medio total en el sistema.
 
## Los escalones de optimización
 
La escalera sube de la mejora más barata a la más costosa, y cada escalón se mide contra el baseline y contra el anterior.
 
| Escalón | Técnica | Qué ataca | Por qué va en ese orden |
| --- | --- | --- | --- |
| 0 | Baseline ingenuo: Python puro, objetos y listas | Nada: es el punto de referencia | Fija el resultado correcto y el tiempo base; se valida contra la teoría |
| 1 | Estructuras de datos y algoritmo: deque, heapq, __slots__ | Complejidad algorítmica (por ejemplo list.pop(0) es O(n)) | Mayor ganancia con menor costo: antes de compilar, mejorar el algoritmo |
| 2 | Python idiomático: variables locales, generadores, menos llamadas | Overhead del intérprete en el bucle caliente | Ganancia moderada; muestra el costo en legibilidad |
| 3 | NumPy: generar tiempos de llegada y servicio en bloque, suma acumulada (add.accumulate) | Bucles en Python puro | Vectoriza lo que se puede; la recurrencia de la cola es secuencial y no se vectoriza de forma directa, lo que es un hallazgo en sí |
| 4 | Numba (JIT) sobre el bucle secuencial | Lo que NumPy no pudo resolver | Mayor salto esperado, con costo en warm-up de compilación y dependencias |
| 5 | Paralelismo: réplicas Monte Carlo con multiprocessing | Uso de varios núcleos | Se paraleliza al final, sobre código ya eficiente; se analiza con la ley de Amdahl |
| 6 (opcional) | Extensión nativa: Cython o Rust | Límite de lo que logra Python | Solo si sobra tiempo; compara contra Numba |
 
De forma transversal, pytest-benchmark en CI hace fallar el pipeline si un cambio empeora los tiempos por encima de un umbral (regresión de rendimiento).
 
Resultado central del informe: una tabla de **speedup contra costo** (líneas de código, complejidad ciclomática con radon, dependencias nuevas) que muestre cuándo vale la pena subir cada escalón.
 
## Metodología y replicabilidad
 
Los resultados centrales serán ratios de speedup y tendencias, no segundos absolutos, porque los tiempos cambian de una PC a otra pero las conclusiones relativas se pueden replicar.
 
- **Entradas idénticas:** los tiempos de llegada y de servicio se generan una vez con np.random.default_rng(seed) y se pasan a todas las versiones; en las réplicas paralelas se derivan semillas con SeedSequence.spawn().
 
- **Corrección primero:** cada escalón debe dar el mismo resultado que el baseline y acercarse a la fórmula teórica antes de medir su tiempo.
 
- **Medición rigurosa:** time.perf_counter(), descarte del warm-up de Numba, entre 7 y 30 repeticiones por medición, y reporte de mediana y rango intercuartil.
 
- **Escalabilidad:** tamaños de 10³ a 10⁷ requests para ver cómo crece cada versión.
 
- **Registro del entorno:** cada corrida guarda un env.json con CPU, núcleos, RAM, sistema operativo y versiones de Python, NumPy y Numba.
 
- **Un solo comando:** python -m scripts.run_all --mode quick (2 a 3 minutos, para verificar) o --mode full (corrida completa para el informe).
 
- **Entorno bloqueado:** Python y dependencias fijadas con uv.lock.
 
- **Docker:** para tests y CI; las mediciones finales se hacen nativas, porque en Windows y macOS Docker corre en una máquina virtual y distorsiona el multiprocessing.
 
- **Qué se mide:** tiempo, speedup, memoria (tracemalloc), error contra la teoría y costo de mantenimiento (radon).
 
## Cumplimiento de la consigna
 
La propuesta cubre cada requisito de la consigna; los puntos marcados como pendientes dependen de datos del grupo o del docente.
 
| Requisito de la consigna | Cómo lo cumple la propuesta |
| --- | --- |
| Grupo de 2 a 4 integrantes | Pendiente: confirmar integrantes; el reparto de tareas está pensado para 2 a 4 personas |
| Presentación en la clase 15, con correcciones para la entrega final en la clase 16 | Pendiente: acordar los hitos en el plan de trabajo |
| Temática relacionada con la asignatura, en el contexto de la ingeniería del software | Rendimiento figura entre las áreas sugeridas; el ángulo de ingeniería está en los trade-offs, los tests de corrección y la regresión de rendimiento en CI |
| Todo el código en Python, con buenas prácticas y herramientas vistas en la cursada | Python con tests (pytest), type hints, linters, radon, entorno bloqueado con uv.lock y pipeline de CI; conviene alinear la lista exacta con lo visto en clase |
| Consultar dudas con el tutor | Pendiente: validar con el docente que el simulador de colas encaja como caso de estudio |
 
## Reparto de tareas y próximos pasos
 
El trabajo se puede repartir en cuatro frentes; con menos integrantes, se combinan.
 
| Frente | Responsabilidad |
| --- | --- |
| Baseline y tests | Escalón 0, theory.py con las fórmulas M/M/1 y M/M/c, tests de corrección |
| Optimización algorítmica y NumPy | Escalones 1 a 3 |
| Numba y paralelismo | Escalones 4 y 5, análisis de speedup y eficiencia |
| Benchmarks, CI e informe | Harness de medición, env.json, pytest-benchmark, gráficos y redacción |
 
Próximos pasos:
 
- ☐ Completar los nombres de los integrantes en la carátula del .pptx.
 
- ☐ Validar con el tutor el simulador de colas como caso de estudio.
 
- ☐ Ajustar los motivos de la diapositiva 2 con las razones reales del grupo.
 
- ☐ Elegir la PC en la que se harán las mediciones finales.
 
- ☐ Crear el repositorio con la estructura base y el baseline con sus tests.
 
- ☐ Ensayar la presentación y repartir quién expone cada diapositiva.
