import numpy as np
import pytest

from queue_sim import step0_naive as step0
from queue_sim import step1_datastructs as step1
from queue_sim import step2_idiomatic as step2
from queue_sim import step3_numpy as step3
from queue_sim.metrics import metrics
from queue_sim.theory import mm1, mmc
from queue_sim.workload import generate_workload, spawn_seeds

# En fases siguientes solo se agregan escalones a esta lista.
STEPS = [step0.simulate, step1.simulate, step2.simulate, step3.simulate]
IDS = [f.__module__.rsplit(".", 1)[-1] for f in STEPS]


@pytest.mark.parametrize("simulate", STEPS, ids=IDS)
def test_determinista_c1(simulate):
    arrivals = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    services = np.array([3.0, 1.0, 1.0, 1.0, 1.0])
    waits = simulate(arrivals, services, 1)
    assert np.allclose(waits, [0, 2, 2, 2, 2], rtol=1e-9)


@pytest.mark.parametrize("simulate", STEPS, ids=IDS)
def test_determinista_c2(simulate):
    arrivals = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    services = np.array([5.0, 5.0, 1.0, 1.0, 1.0])
    waits = simulate(arrivals, services, 2)
    assert np.allclose(waits, [0, 0, 3, 3, 2], rtol=1e-9)


@pytest.mark.parametrize("simulate", STEPS, ids=IDS)
@pytest.mark.parametrize("servers", [1, 2, 3])
def test_invariantes(simulate, servers):
    arrivals, services = generate_workload(5000, 0.7 * servers, 1.0, seed=3)
    w1 = simulate(arrivals, services, servers)
    w2 = simulate(arrivals, services, servers)
    assert w1.shape == arrivals.shape
    assert np.all(w1 >= 0)
    assert np.array_equal(w1, w2)


@pytest.mark.parametrize("simulate", STEPS, ids=IDS)
@pytest.mark.parametrize("servers", [1, 3])
def test_contra_teoria(simulate, servers):
    """Criterio estadistico (D4): media de Wq y W dentro de 3 errores estandar (R=20)."""
    rho, mu, n, reps = 0.7, 1.0, 200_000, 20
    lam = rho * servers * mu
    esperado = mm1(lam, mu) if servers == 1 else mmc(lam, mu, servers)
    wq, w = [], []
    for seed in spawn_seeds(2026, reps):
        arrivals, services = generate_workload(n, lam, mu, seed)
        m = metrics(simulate(arrivals, services, servers), services, servers)
        wq.append(m["mean_wait"])
        w.append(m["mean_sojourn"])
    for muestras, teorico in ((wq, esperado["Wq"]), (w, esperado["W"])):
        se = np.std(muestras, ddof=1) / np.sqrt(reps)
        assert abs(np.mean(muestras) - teorico) <= 3 * se


@pytest.mark.parametrize("simulate", STEPS[1:], ids=IDS[1:])
@pytest.mark.parametrize("servers", [1, 2, 3, 8])
def test_igual_al_baseline(simulate, servers):
    """D4: cada escalon coincide con el baseline (allclose, rtol=1e-9)."""
    arrivals, services = generate_workload(100_000, 0.75 * servers, 1.0, seed=11)
    esperado = step0.simulate(arrivals, services, servers)
    assert np.allclose(simulate(arrivals, services, servers), esperado, rtol=1e-9)
