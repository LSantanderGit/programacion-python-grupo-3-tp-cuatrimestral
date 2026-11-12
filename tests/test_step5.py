import numpy as np

from queue_sim.step5_parallel import simulate_replicas, simulate_replicas_serial
from queue_sim.workload import spawn_seeds


def test_step5_replicas_coinciden_con_serie():
    """Verifica que la ejecucion en paralelo da los mismos resultados exactos que en serie."""
    n_requests = 10_000
    arrival_rate = 1.4
    service_rate = 1.0
    servers = 2
    seeds = spawn_seeds(42, 4)

    res_serial = simulate_replicas_serial(
        n_requests, arrival_rate, service_rate, servers, seeds
    )
    res_parallel = simulate_replicas(
        n_requests, arrival_rate, service_rate, servers, seeds, max_workers=2
    )

    assert len(res_parallel) == len(res_serial) == 4
    for par, ser in zip(res_parallel, res_serial):
        assert np.array_equal(par, ser)
