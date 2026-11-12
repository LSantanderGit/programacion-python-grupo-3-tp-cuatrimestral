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
