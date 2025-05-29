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
    ([2, 0], 100, math.sqrt(100*60/(4*math.pi))),  # 正常系
    ([1, 0, 0], 0, 0.0),  # 2次式で解が0のみ
    ([1, 0], -100, 0.0),  # shaft_power負→正の解なし
    ([1, 0], 1e10, 0.0),  # 解が非常に大きく物理的に不適切→0
    ([1, 0, 1], 0, 0.0),  # 複素数解のみ
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
    # 有効風速8, P=512, T=2r, 効率1, 電圧10, カットイン0
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 0)
    # rpm = sqrt(512*60/(4pi))
    import math
    rpm = math.sqrt(512*60/(4*math.pi))
    expected = rpm * 10.0
    assert p.value == pytest.approx(expected)


def test_calculate_instantaneous_power_cut_in():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 8, 0)
    # カットイン回転数を大きく
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 1e4)
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
