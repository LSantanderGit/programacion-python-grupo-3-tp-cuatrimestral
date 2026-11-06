import numpy as np
import pytest

from queue_sim.workload import generate_workload, spawn_seeds


def test_reproducible_por_semilla():
    a1, s1 = generate_workload(1000, 0.7, 1.0, seed=42)
    a2, s2 = generate_workload(1000, 0.7, 1.0, seed=42)
    assert np.array_equal(a1, a2) and np.array_equal(s1, s2)
    a3, _ = generate_workload(1000, 0.7, 1.0, seed=43)
    assert not np.array_equal(a1, a3)


def test_estadistica_exponencial():
    n = 200_000
    arrivals, services = generate_workload(n, 0.7, 1.0, seed=1)
    assert np.all(np.diff(arrivals) > 0)
    interarribos = np.diff(arrivals, prepend=0.0)
    assert interarribos.mean() == pytest.approx(1 / 0.7, rel=0.02)
    assert services.mean() == pytest.approx(1.0, rel=0.02)
    # exponencial: desvio estandar ~ media
    assert services.std() == pytest.approx(1.0, rel=0.03)


def test_spawn_seeds_independientes_y_reproducibles():
    s1, s2 = spawn_seeds(7, 3), spawn_seeds(7, 3)
    assert len(s1) == 3
    w = [generate_workload(10, 1.0, 2.0, s)[0] for s in s1]
    w2 = [generate_workload(10, 1.0, 2.0, s)[0] for s in s2]
    for x, y in zip(w, w2):
        assert np.array_equal(x, y)
    assert not np.array_equal(w[0], w[1])


def test_parametros_invalidos():
    with pytest.raises(ValueError):
        generate_workload(0, 1.0, 1.0, 1)
    with pytest.raises(ValueError):
        generate_workload(10, 0.0, 1.0, 1)
