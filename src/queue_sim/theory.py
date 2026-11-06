"""Resultados analiticos de teoria de colas: M/M/1 y M/M/c (Erlang C)."""

import math


def _validate(arrival_rate: float, service_rate: float, servers: int) -> None:
    if servers < 1:
        raise ValueError("La cantidad de servidores debe ser al menos 1")
    if arrival_rate <= 0 or service_rate <= 0:
        raise ValueError("Las tasas de llegada y de servicio deben ser positivas")
    if arrival_rate >= servers * service_rate:
        raise ValueError(
            "Sistema inestable: se requiere lambda < c*mu "
            f"(lambda={arrival_rate}, c*mu={servers * service_rate})"
        )


def mm1(arrival_rate: float, service_rate: float) -> dict[str, float]:
    """M/M/1: devuelve ``rho``, espera en cola ``Wq`` y tiempo en el sistema ``W``."""
    _validate(arrival_rate, service_rate, 1)
    rho = arrival_rate / service_rate
    wq = rho / (service_rate - arrival_rate)
    return {"rho": rho, "Wq": wq, "W": wq + 1.0 / service_rate}


def mmc(arrival_rate: float, service_rate: float, servers: int) -> dict[str, float]:
    """M/M/c con Erlang C.

    Devuelve ``rho`` (utilizacion por servidor), ``P_wait`` (probabilidad de esperar),
    ``Wq`` (espera media en cola) y ``W`` (tiempo medio en el sistema).
    """
    _validate(arrival_rate, service_rate, servers)
    a = arrival_rate / service_rate
    rho = a / servers
    ultimo = a**servers / math.factorial(servers) / (1.0 - rho)
    suma = sum(a**k / math.factorial(k) for k in range(servers))
    p_wait = ultimo / (suma + ultimo)
    wq = p_wait / (servers * service_rate - arrival_rate)
    return {"rho": rho, "P_wait": p_wait, "Wq": wq, "W": wq + 1.0 / service_rate}
