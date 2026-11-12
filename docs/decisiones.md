# Decisiones tecnicas

Formato: D#: decision, razon, fecha.

- **D1**: Para c servidores, cada request va al worker que se libera primero: `inicio = max(llegada, min(libres))`, `libres[argmin] = inicio + servicio`. Razon: Lindley (`W[i+1] = max(0, W[i] + S[i] - A[i+1])`) solo vale para c=1. Fecha: 2026-11-06.
- **D2**: Baseline por eventos, ingenuo pero razonable (objeto `Request` por llegada, listas, busqueda lineal del worker libre). No usar reloj discretizado. Razon: el reloj discretizado agrega error de discretizacion contra la teoria. Debe documentarse en el docstring por que no es un hombre de paja. Fecha: 2026-11-06.
- **D3**: Contrato `simulate(arrivals, services, servers) -> waits` (np.ndarray de esperas en cola, uno por request). Metricas (media de espera, tiempo medio en el sistema, p95, utilizacion) en `metrics()` comun, misma definicion de percentil para todos los escalones. Razon: comparabilidad; se mide `simulate` aparte de `metrics`. Fecha: 2026-11-06.
- **D4**: Entre escalones y baseline: `np.allclose(rtol=1e-9)`. Contra teoria: criterio estadistico (~3 errores estandar sobre R replicas). Razon: el primero es determinista, la segunda es estocastica. Fecha: 2026-11-06.
- **D5**: Validar con rho entre 0.5 y 0.8; descartar transitorio inicial (parametro, 5 % por defecto). Barrido rho 0.5-0.9 solo en capacity planning. Razon: reducir sesgo de arranque. Fecha: 2026-11-06.
- **D6**: Matriz de tamanos: baseline y escalon 2 hasta 10^6; escalones 3, 4 y 5 hasta 10^7. Se define en `benchmarks/config.py` (Fase 4). Razon: tiempos del baseline. Fecha: 2026-11-06.
- **D7**: Cada replica genera sus entradas con semilla hija (`SeedSequence.spawn`). Speedup paralelo contra las mismas R replicas en serie con el escalon 4. Windows (`spawn`): todo bajo `if __name__ == "__main__"`, funciones top-level, `ProcessPoolExecutor`. Fecha: 2026-11-06.
- **D8**: CPU hibrida (i9 13.a gen, nucleos P y E): curva de eficiencia no lineal. Medir con 1, 2, 4, 8, 16 y N logicos; reportar el codo. `env.json` registra el modelo exacto de CPU. Fecha: 2026-11-06.
- **D9**: CI en GitHub Actions: matriz ubuntu-latest + windows-latest, Python 3.12; ruff, pytest y benchmark de humo. Regresion de rendimiento por ratios, nunca tiempos absolutos (runners ruidosos). Fecha: 2026-11-06.
- **D10**: Documentacion, README, docstrings, comentarios y mensajes en espanol; identificadores en ingles. Fecha: 2026-11-06.
- **D11**: Sin escalon 6 ni segundo caso de estudio. Dashboard HTML (plotly) solo si sobra tiempo. Fecha: 2026-11-06.
- **D12**: Informe en Google Docs. `make_report.py` genera figuras PNG 300 dpi ("Grafico 1, 2..."), tablas ("Tabla I, II...") y borradores por capitulo en `report/`. Fecha: 2026-11-06.

## Decisiones tomadas en las Fases 0 y 1 (no estaban en el prompt)

- **D13**: `docs/CONTEXTO.md` no existia en el repo; estructura inferida del prompt y CONTEXTO.md minimo creado como resumen. Fecha: 2026-11-06.
- **D14**: Python fijado a `>=3.12,<3.13`; build backend hatchling con layout `src/`. Versiones resueltas por uv (ver uv.lock): numpy 2.5.4, numba 0.68.1. Fecha: 2026-11-06.
- **D15**: `metrics()` calcula utilizacion como `sum(services)/(servers*makespan)` sobre todos los requests; con `makespan=None` devuelve `nan`. Se agrega `makespan(arrivals, waits, services)` como ayudante. Razon: la firma pedida no recibe `arrivals`. Fecha: 2026-11-06.
- **D16**: Test contra teoria usa rho=0.7, n=200_000, R=20, semilla base 2026 y `|media - teorico| <= 3*EE` (EE = desvio/sqrt(R)). Fecha: 2026-11-06.
- **D17**: Escalon 3 usa Lindley vectorizado (cumsum + minimum.accumulate) solo para c=1; para c>1 reutiliza el bucle del escalon 2, porque el estado es un vector de c tiempos con argmin y no admite scan. Por eso el escalon 3 no acelera c>1. Fecha: 2026-11-06.

## Decisiones tomadas en la Fase 3

- **D18**: Escalon 4 implementa `_simulate_numba` con `@njit(cache=True)`, seleccionando el servidor libre via `np.argmin` sobre un array de floats. Se incluye `warmup()` para compilar previamente y medir el costo JIT de forma aislada. Fecha: 2026-11-12.
- **D19**: Escalon 5 implementa `simulate(arrivals, services, servers)` delegando en el kernel de Numba (escalon 4) para satisfacer el contrato comun D3, y provee `simulate_replicas` y `simulate_replicas_serial` para corridas Monte Carlo con `ProcessPoolExecutor`. Se anade parametro `return_metrics` para permitir calcular metricas en el worker y evitar la serializacion por IPC de grandes arrays en Windows (`spawn`). Fecha: 2026-11-12.

## Decisiones tomadas en la Fase 4

- **D20**: En `benchmarks/config.py` y `benchmarks/harness.py`, el perfil `quick` evalua tamanos hasta $10^5$ (3 repeticiones intercaladas) para verificacion de punta a punta en menos de 2 minutos, mientras que `full` escala hasta $10^7$ (7 repeticiones) segun D6. La medicion de mantenibilidad extrae SLOC y complejidad ciclomica (media y maxima) con `radon`. Fecha: 2026-11-12.
- **D21**: El smoke benchmark de CI (`scripts/smoke_benchmark.py`) verifica que el ratio de velocidad del escalon 4 respecto al escalon 1 sea al menos $5.0\times$ sobre entradas compartidas ($n=20\,000, c=2$), aislando las regresiones de rendimiento del ruido inherente a los runners virtuales compartidos. Fecha: 2026-11-12.

## Decisiones tomadas en la Fase 5

- **D22**: `scripts/make_report.py` implementa la generacion automatizada de figuras a 300 DPI (Graficos 1 a 5) y tablas formales en Markdown (Tablas I a VI) leyendo exclusivamente de `results/raw/` sin repetir mediciones. Genera los capitulos del informe y el documento maestro `report/informe_completo.md` listo para Google Docs siguiendo la guia formal de la UAI. Fecha: 2026-11-12.
- **D23**: Se implementa `scripts/make_dashboard.py` y `scripts/serve_dashboard.py` para generar un Dashboard Web Interactivo autocontenido (`results/dashboard.html`) servido localmente. Se anade el parametro `--serve` a `scripts/run_all.py` para permitir la ejecucion integral en un solo paso: tests de correccion, benchmarks, figuras 300 DPI, informe y apertura del dashboard en el navegador. Fecha: 2026-11-12.
