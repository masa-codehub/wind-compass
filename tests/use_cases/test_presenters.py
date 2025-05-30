from wind_compass.use_cases.simulation_use_cases import ScenarioResult
from wind_compass.adapters.ui.presenters import ConsolePresenter
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../src')))


def test_present_multiple_scenarios_matrix():
    presenter = ConsolePresenter()
    results = [
        ScenarioResult(angle=0, annual_power=1000.0),
        ScenarioResult(angle=10, annual_power=1100.0),
        ScenarioResult(angle=20, error_message="calc error"),
    ]
    angles = [0, 10, 20]
    output = presenter.present_multiple_scenarios(results, angles)
    assert "1000.00 kWh" in output
    assert "1100.00 kWh" in output
    assert "Error: calc error" in output
    assert "Angle (deg)" in output
    assert "Annual Power" in output
