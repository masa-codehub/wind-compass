from wind_compass.domain.models import Power, Energy, Torque, EffectiveWindSpeed
import pytest


def test_power_value_and_unit():
    p = Power(100.0)
    assert p.value == 100.0
    assert isinstance(p, Power)


def test_power_addition():
    p1 = Power(50.0)
    p2 = Power(70.0)
    p3 = p1 + p2
    assert isinstance(p3, Power)
    assert p3.value == 120.0


def test_power_addition_with_invalid_type():
    p = Power(1.0)
    with pytest.raises(TypeError):
        _ = p + 10  # int
    with pytest.raises(TypeError):
        _ = p + "string"  # str


@pytest.mark.parametrize("v1,v2", [
    (100.0, 30.0),
    (0.0, 0.0),
    (-10.0, 10.0)
])
def test_power_subtraction(v1, v2):
    p1 = Power(v1)
    p2 = Power(v2)
    p3 = p1 - p2
    assert isinstance(p3, Power)
    assert p3.value == pytest.approx(v1 - v2)


def test_power_subtraction_with_invalid_type():
    p = Power(1.0)
    with pytest.raises(TypeError):
        _ = p - 10
    with pytest.raises(TypeError):
        _ = p - None


def test_power_equality():
    assert Power(10.0) == Power(10.0)
    assert Power(10.0) != Power(11.0)


def test_power_equality_with_invalid_type():
    p = Power(1.0)
    assert (p == "string") is False
    assert (p == object()) is False


def test_energy_value_and_unit():
    e = Energy(500.0)
    assert e.value == 500.0
    assert isinstance(e, Energy)


def test_energy_addition():
    e1 = Energy(100.0)
    e2 = Energy(200.0)
    e3 = e1 + e2
    assert isinstance(e3, Energy)
    assert e3.value == 300.0


def test_energy_addition_with_invalid_type():
    e = Energy(1.0)
    with pytest.raises(TypeError):
        _ = e + 10
    with pytest.raises(TypeError):
        _ = e + None


def test_torque_value_and_unit():
    t = Torque(12.5)
    assert t.value == 12.5
    assert isinstance(t, Torque)


def test_effective_wind_speed_value():
    w = EffectiveWindSpeed(8.2)
    assert w.value == 8.2
    assert isinstance(w, EffectiveWindSpeed)


def test_power_invalid_type():
    p = Power(10.0)
    assert (p == 10.0) is False
    assert (p == None) is False


def test_energy_invalid_type():
    e = Energy(10.0)
    assert (e == 10.0) is False
    assert (e == None) is False


def test_torque_invalid_type():
    t = Torque(1.0)
    assert (t == 1.0) is False
    assert (t == None) is False


def test_effective_wind_speed_invalid_type():
    w = EffectiveWindSpeed(1.0)
    assert (w == 1.0) is False
    assert (w == None) is False


def test_power_immutable():
    p = Power(1.0)
    with pytest.raises(Exception):
        p.value = 2.0


def test_energy_immutable():
    e = Energy(1.0)
    with pytest.raises(Exception):
        e.value = 2.0


def test_torque_immutable():
    t = Torque(1.0)
    with pytest.raises(Exception):
        t.value = 2.0


def test_effective_wind_speed_immutable():
    w = EffectiveWindSpeed(1.0)
    with pytest.raises(Exception):
        w.value = 2.0


def test_power_equality_with_invalid_type():
    p = Power(1.0)
    assert (p == "string") is False
    assert (p == object()) is False


def test_energy_equality_with_invalid_type():
    e = Energy(1.0)
    assert (e == "string") is False
    assert (e == object()) is False


def test_torque_equality_with_invalid_type():
    t = Torque(1.0)
    assert (t == "string") is False
    assert (t == object()) is False


def test_effective_wind_speed_equality_with_invalid_type():
    w = EffectiveWindSpeed(1.0)
    assert (w == "string") is False
    assert (w == object()) is False
