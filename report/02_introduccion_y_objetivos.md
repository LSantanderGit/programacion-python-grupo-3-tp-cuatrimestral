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
