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
