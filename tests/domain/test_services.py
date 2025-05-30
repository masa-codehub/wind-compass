from wind_compass.domain.services import PowerGenerationSimulator
from wind_compass.domain.models import PowerPlantModel, PolynomialCurve, Power, Torque, EffectiveWindSpeed, WindReading
from datetime import datetime
import math
import pytest


def test_effective_wind_speed_calc():
    sim = PowerGenerationSimulator(None)
    eff = sim._calculate_effective_wind_speed(10, 0, 0)
    assert eff == pytest.approx(10)
    eff = sim._calculate_effective_wind_speed(10, 90, 0)
    assert eff == pytest.approx(0)
    eff = sim._calculate_effective_wind_speed(10, 180, 0)
    assert eff == pytest.approx(0)  # 追い風は0になる仕様


def test_turbine_power_calc():
    power_curve = PolynomialCurve([1, 0, 0, 0])  # v^3
    model = PowerPlantModel(
        power_curve, PolynomialCurve([1]), PolynomialCurve([1]))
    sim = PowerGenerationSimulator(model)
    p = sim._calculate_turbine_power(8)
    assert p == pytest.approx(512)


@pytest.mark.parametrize("coeffs, shaft_power, expected", [
    # krpm→rpm変換後の期待値に修正
    # torque_curve: [2, 0] (2*krpm), shaft_power=100
    # T(rpm) = 2*(rpm/1000) = 0.002*rpm
    # P = T*rpm*2pi/60 = 0.002*rpm^2*2pi/60 = shaft_power
    # rpm^2 = shaft_power*60/(0.004*pi)
    ([2, 0], 100, math.sqrt(100*60/(0.004*math.pi))),
    ([1, 0, 0], 0, 0.0),
    ([1, 0], -100, 0.0),
    ([1, 0], 1e10, 0.0),
    ([1, 0, 1], 0, 0.0),
])
def test_rpm_solver_cases(coeffs, shaft_power, expected):
    torque_curve = PolynomialCurve(coeffs)
    sim = PowerGenerationSimulator(None)
    rpm = sim._solve_for_rpm(shaft_power, torque_curve)
    assert rpm == pytest.approx(expected)


def make_model():
    # P = v^3, T = 2r, I = r
    return PowerPlantModel(
        PolynomialCurve([1, 0, 0, 0]),  # v^3
        PolynomialCurve([2, 0]),        # 2r
        PolynomialCurve([1, 0])         # r
    )


def test_calculate_instantaneous_power_normal():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 8, 0)
    # 有効風速8, P=512, T=2r, I=r, 効率1, 電圧10, カットイン0
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 0)
    import math
    rpm = math.sqrt(512*60/(0.004*math.pi))
    expected = (rpm / 1000) * 10.0  # I = rpm/1000, P = I*V
    assert p.value == pytest.approx(expected)


def test_calculate_instantaneous_power_cut_in():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 8, 0)
    # カットイン回転数を大きく
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 1e6)
    assert p.value == 0.0


def test_calculate_instantaneous_power_zero_efficiency():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 8, 0)
    p = sim.calculate_instantaneous_power(wind, 0, 0.0, 10.0, 0)
    assert p.value == 0.0


def test_calculate_instantaneous_power_zero_voltage():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 8, 0)
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 0.0, 0)
    assert p.value == 0.0


def test_calculate_instantaneous_power_zero_wind():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 0, 0)
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 0)
    assert p.value == 0.0


def test_calculate_instantaneous_power_negative_wind():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), -5, 0)
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 0)
    assert p.value == 0.0


def test_calculate_instantaneous_power_backwind():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 10, 180)
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 0)
    assert p.value == 0.0
