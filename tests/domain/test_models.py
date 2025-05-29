from wind_compass.domain.models import PolynomialCurve, PowerPlantModel
import pytest


def test_polynomial_curve_calculate():
    # 2次式: 2x^2 + 3x + 4
    curve = PolynomialCurve([2, 3, 4])
    assert curve.calculate(0) == 4
    assert curve.calculate(1) == 2 + 3 + 4  # 9
    assert curve.calculate(2) == 2*4 + 3*2 + 4  # 8+6+4=18


def test_power_plant_model_holds_curves():
    power_curve = PolynomialCurve([1, 0, 0])  # x^2
    torque_curve = PolynomialCurve([0, 1, 0])  # x
    current_curve = PolynomialCurve([0, 0, 1])  # 1
    model = PowerPlantModel(
        power_curve=power_curve,
        torque_curve=torque_curve,
        current_curve=current_curve
    )
    assert model.power_curve is power_curve
    assert model.torque_curve is torque_curve
    assert model.current_curve is current_curve
    assert model.power_curve.calculate(2) == 4
    assert model.torque_curve.calculate(2) == 2
    assert model.current_curve.calculate(2) == 1


def test_polynomial_curve_typeerror_on_non_list():
    with pytest.raises(TypeError):
        PolynomialCurve(None)
    with pytest.raises(TypeError):
        PolynomialCurve(123)
    with pytest.raises(TypeError):
        PolynomialCurve("abc")


def test_polynomial_curve_typeerror_on_non_number_elements():
    with pytest.raises(TypeError):
        PolynomialCurve([1, "a", 3])
    with pytest.raises(TypeError):
        PolynomialCurve([object(), 2.0])


def test_polynomial_curve_valueerror_on_empty():
    with pytest.raises(ValueError):
        PolynomialCurve([])


def test_power_plant_model_typeerror_on_non_curve():
    with pytest.raises(TypeError):
        PowerPlantModel(1, 2, 3)
    with pytest.raises(TypeError):
        PowerPlantModel("a", "b", "c")


def test_wind_reading_fields():
    from wind_compass.domain.models import WindReading
    from datetime import datetime
    dt = datetime(2024, 1, 1, 0, 0, 0)
    w = WindReading(dt, 10.0, 270.0)
    assert w.observed_at == dt
    assert w.wind_speed == 10.0
    assert w.wind_direction == 270.0


def test_wind_reading_immutable():
    from wind_compass.domain.models import WindReading
    from datetime import datetime
    w = WindReading(datetime(2024, 1, 1, 0, 0, 0), 10.0, 270.0)
    with pytest.raises(Exception):
        w.wind_speed = 5.0
