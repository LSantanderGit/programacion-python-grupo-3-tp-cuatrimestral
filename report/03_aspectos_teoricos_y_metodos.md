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
