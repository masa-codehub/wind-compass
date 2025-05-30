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
    power_curve = PolynomialCurve([1, 0, 0, 0])  # v^3 (coeffs for v^3, v^2, v, const)
    # For torque and current curves, provide valid 4-element lists even if not used in this specific test
    model = PowerPlantModel(
        power_curve, PolynomialCurve([0,0,1,0]), PolynomialCurve([0,0,1,0]))
    sim = PowerGenerationSimulator(model)
    p = sim._calculate_turbine_power(8)
    assert p == pytest.approx(512)


@pytest.mark.parametrize("coeffs, shaft_power, expected", [
    # torque_curve: T(krpm) = 2*krpm -> coeffs = [0,0,2,0]
    # T(rpm) = 2*(rpm/1000) = 0.002*rpm
    # P = T*rpm*2pi/60 = 0.002*rpm^2*2pi/60 = shaft_power
    # rpm^2 = shaft_power*60/(0.004*pi)
    ([0,0,2,0], 100, math.sqrt(100*60/(0.004*math.pi))), # approx 690.988
    # T(krpm) = 1*krpm^2 -> coeffs = [0,1,0,0]
    ([0,1,0,0], 0, 0.0),
    # T(krpm) = 1*krpm -> coeffs = [0,0,1,0]
    ([0,0,1,0], -100, 0.0), # Negative shaft power, expect 0 rpm
    # T(krpm) = 1*krpm -> coeffs = [0,0,1,0], P = 1e10. rpm_calc > 1e4, so expect 0.0
    ([0,0,1,0], 1e10, 0.0),
    # T(krpm) = 1*krpm^2 + 1 -> coeffs = [0,1,0,1]
    ([0,1,0,1], 0, 0.0), # Solves to rpm = 0
])
def test_rpm_solver_cases(coeffs, shaft_power, expected):
    # Ensure coeffs are always 4 elements for PolynomialCurve if that's the convention
    # However, PolynomialCurve itself only checks for non-empty.
    # JsonConfigReader enforces 4 coeffs. Tests should ideally mirror this.
    # The coeffs provided in parametrize are already 4-elements.
    # The coeffs_fixed line is fine, it will just take coeffs as is.
    coeffs_fixed = coeffs + [0.0] * \
        (4 - len(coeffs)) if len(coeffs) < 4 else coeffs[:4]
    torque_curve = PolynomialCurve(coeffs_fixed)
    sim = PowerGenerationSimulator(None) # model is not used by _solve_for_rpm directly
    rpm = sim._solve_for_rpm(shaft_power, torque_curve)
    assert rpm == pytest.approx(expected)


def make_model():
    # P_turbine(v_eff) = v_eff^3 -> coeffs = [1,0,0,0] (for v^3, v^2, v, const)
    # T_gen(R_krpm) = 2*R_krpm -> coeffs = [0,0,2,0] (for R^3, R^2, R, const in krpm)
    # I_gen(R_krpm) = 1*R_krpm -> coeffs = [0,0,1,0] (for R^3, R^2, R, const in krpm)
    return PowerPlantModel(
        PolynomialCurve([1, 0, 0, 0]),
        PolynomialCurve([0, 0, 2, 0]),  # Generator Torque curve: T(krpm) = 2*krpm
        PolynomialCurve([0, 0, 1, 0])   # Generator Current curve: I(krpm) = 1*krpm
    )


def test_calculate_instantaneous_power_normal():
    model = make_model() # Uses T(krpm) = 2*krpm and I(krpm) = 1*krpm
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 8, 0) # eff_ws = 8
    # P_turbine = 8^3 = 512
    # shaft_power (to gen) = 512 * efficiency (1.0 here) = 512
    # _solve_for_rpm with T(krpm)=2*krpm for shaft_power=512:
    # rpm_gen_expected = sqrt(512*60 / (0.004*math.pi)) approx 1560.26 rpm
    # Current I = (rpm_gen_expected/1000) * 1 (from I(krpm)=1*krpm)
    # Final Power P = I * voltage (10.0 here)
    # So, P_final = (rpm_gen_expected/1000) * 1 * 10.0
    
    # calculate_instantaneous_power takes efficiency, voltage, cut_in_rpm
    # The gear_ratio argument was removed in previous iterations as per user direction.
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 0) 
                                        # turbine_angle, efficiency, voltage, cut_in_rpm
    
    rpm_gen_calc = math.sqrt(512*60/(0.004*math.pi)) # This is rpm_gen
    expected_current = (rpm_gen_calc / 1000) * 1.0 # I(krpm) = 1*krpm
    expected_final_power = expected_current * 10.0
    assert p.value == pytest.approx(expected_final_power)


def test_calculate_instantaneous_power_cut_in():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 8, 0)
    # Cut-in RPM is high
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 1e6) # gear_ratio removed
    assert p.value == 0.0


def test_calculate_instantaneous_power_zero_efficiency():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 8, 0)
    p = sim.calculate_instantaneous_power(wind, 0, 0.0, 10.0, 0) # efficiency = 0
    assert p.value == 0.0


def test_calculate_instantaneous_power_zero_voltage():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 8, 0)
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 0.0, 0) # voltage = 0
    assert p.value == 0.0


def test_calculate_instantaneous_power_zero_wind():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 0, 0) # wind_speed = 0
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 0)
    assert p.value == 0.0


def test_calculate_instantaneous_power_negative_wind():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), -5, 0) # negative wind_speed
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 0)
    assert p.value == 0.0


def test_calculate_instantaneous_power_backwind():
    model = make_model()
    sim = PowerGenerationSimulator(model)
    wind = WindReading(datetime(2024, 1, 1, 0, 0, 0), 10, 180) # backwind
    p = sim.calculate_instantaneous_power(wind, 0, 1.0, 10.0, 0)
    assert p.value == 0.0