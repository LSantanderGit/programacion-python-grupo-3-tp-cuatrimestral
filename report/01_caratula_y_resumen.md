# Trabajo de Investigación: Escalera de Optimización en Python

**Universidad Abierta Interamericana (UAI)**  
**Facultad de Tecnología Informática**  
**Asignatura:** 69 - Optativa - Programación II  
**Turno:** Noche | **Sede:** Regional Norte  

**Alumnos:**
- José Manuel Balderrama Mariscal
- Ramiro Busto
- Micaela Escobar Lyon
- Nicolas Torcuato Alberto Maciel
- Lucas Matías Santander

**Profesor Titular:** Ing. Gastón Matías Weingand  
**Año:** 2026 | Buenos Aires, Argentina  

---

## Resumen

El presente trabajo de investigación experimental evalúa el impacto en rendimiento y el costo de mantenimiento de seis técnicas progresivas de optimización en Python aplicadas a un simulador de colas de eventos discretos ($M/M/1$ y $M/M/c$) para *capacity planning*. Se recorre la "escalera de optimización" comenzando desde un *baseline* orientado a objetos en Python puro, transitando por estructuras algorítmicas adecuadas (`heapq`, `__slots__`), optimizaciones idiomáticas del intérprete, vectorización con NumPy, compilación nativa JIT con Numba y paralelismo Monte Carlo con `multiprocessing`. Cada escalón se valida rigurosamente contra el modelo analítico de teoría de colas (Erlang C) y contra el *baseline* mediante pruebas automatizadas con tolerancia $10^{-9}$. Los resultados evidencian que Numba logra una aceleración superior a dos órdenes de magnitud ($>130\times$) eliminando la sobrecarga secuencial que NumPy no puede vectorizar, mientras que el paralelismo multiproceso exhibe una meseta explicada por la ley de Amdahl y la sobrecarga de arranque (*spawn*) e IPC en Windows. El estudio proporciona criterios cuantitativos para decidir cuándo es ingenierilmente conveniente escalar cada peldaño de optimización.
