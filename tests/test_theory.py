import pytest

from queue_sim.theory import mm1, mmc


def test_mm1_valores_conocidos():
    r = mm1(0.7, 1.0)
    assert r["rho"] == pytest.approx(0.7)
    assert r["Wq"] == pytest.approx(0.7 / 0.3)
    assert r["W"] == pytest.approx(0.7 / 0.3 + 1.0)


def test_mmc_con_c1_coincide_con_mm1():
    a, b = mm1(0.6, 1.0), mmc(0.6, 1.0, 1)
    assert b["Wq"] == pytest.approx(a["Wq"])
    assert b["W"] == pytest.approx(a["W"])
    assert b["P_wait"] == pytest.approx(a["rho"])


def test_mmc_c2_a_mano():
    # lambda=1, mu=1, c=2: a=1, rho=0.5, Erlang C = 1/3, Wq = (1/3)/(2-1) = 1/3
    r = mmc(1.0, 1.0, 2)
    assert r["rho"] == pytest.approx(0.5)
    assert r["P_wait"] == pytest.approx(1 / 3)
    assert r["Wq"] == pytest.approx(1 / 3)
    assert r["W"] == pytest.approx(4 / 3)


@pytest.mark.parametrize("args", [(1.0, 1.0, 1), (2.0, 1.0, 2), (3.0, 1.0, 2)])
def test_inestable_lanza_value_error(args):
    with pytest.raises(ValueError, match="inestable"):
        mmc(*args)


def test_parametros_invalidos():
    with pytest.raises(ValueError):
        mmc(1.0, 1.0, 0)
    with pytest.raises(ValueError):
        mm1(-1.0, 1.0)
