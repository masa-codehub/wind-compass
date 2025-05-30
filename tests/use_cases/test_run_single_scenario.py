import pytest
from unittest.mock import MagicMock
from datetime import datetime
from wind_compass.domain.constants import DEFAULT_TIME_INTERVAL_HOURS

from wind_compass.use_cases.run_single_scenario import (
    RunSingleSimulationScenarioUseCase, ApplicationError
)
from wind_compass.use_cases.dtos import SingleScenarioInputDTO
from wind_compass.domain.models import WindReading, PowerPlantModel, Power


class DummyPowerPlantModel(PowerPlantModel):
    pass


class DummyWindReading(WindReading):
    pass


def make_input_dto():
    return SingleScenarioInputDTO(
        wind_data_path="dummy_wind.csv",
        config_file_path="dummy_config.json",
        angle=0.0,
        efficiency=0.9,
        voltage=100.0,
        cut_in_rpm=10.0
    )


def test_run_single_scenario_success():
    # Arrange
    wind_readings = [
        WindReading(datetime(2023, 1, 1, 0, 0, 0), 10.0, 0.0),
        WindReading(datetime(2023, 1, 1, 0, 10, 0), 12.0, 0.0)
    ]
    power_plant_model = MagicMock(spec=PowerPlantModel)
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.return_value = wind_readings
    mock_config_reader = MagicMock()
    mock_config_reader.read.return_value = power_plant_model
    mock_simulator = MagicMock()
    mock_simulator.calculate_instantaneous_power.return_value = Power(1000.0)
    simulator_factory = MagicMock(return_value=mock_simulator)
    use_case = RunSingleSimulationScenarioUseCase(
        mock_wind_data_reader, mock_config_reader, simulator_factory
    )
    input_dto = make_input_dto()
    # Act
    output = use_case.execute(input_dto)
    # Assert
    mock_wind_data_reader.read.assert_called_once_with(
        input_dto.wind_data_path)
    mock_config_reader.read.assert_called_once_with(input_dto.config_file_path)
    assert mock_simulator.calculate_instantaneous_power.call_count == 2
    # Δt固定値で2点分
    power_watts = 1000.0
    delta_t_hours = DEFAULT_TIME_INTERVAL_HOURS
    num_data_points = 2
    total_energy_wh = (power_watts * delta_t_hours) * num_data_points
    expected_kwh = total_energy_wh / 1000.0
    assert output.annual_power_kwh == pytest.approx(expected_kwh)


def test_run_single_scenario_wind_file_not_found():
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.side_effect = FileNotFoundError("wind.csv")
    mock_config_reader = MagicMock()
    simulator_factory = MagicMock()
    use_case = RunSingleSimulationScenarioUseCase(
        mock_wind_data_reader, mock_config_reader, simulator_factory
    )
    input_dto = make_input_dto()
    with pytest.raises(ApplicationError, match="Input file not found"):
        use_case.execute(input_dto)


def test_run_single_scenario_config_file_not_found():
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.return_value = [
        WindReading(datetime(2023, 1, 1, 0, 0, 0), 10.0, 0.0)]
    mock_config_reader = MagicMock()
    mock_config_reader.read.side_effect = FileNotFoundError("config.json")
    simulator_factory = MagicMock()
    use_case = RunSingleSimulationScenarioUseCase(
        mock_wind_data_reader, mock_config_reader, simulator_factory
    )
    input_dto = make_input_dto()
    with pytest.raises(ApplicationError, match="Input file not found"):
        use_case.execute(input_dto)


def test_run_single_scenario_invalid_wind_data():
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.side_effect = ValueError("bad wind data")
    mock_config_reader = MagicMock()
    simulator_factory = MagicMock()
    use_case = RunSingleSimulationScenarioUseCase(
        mock_wind_data_reader, mock_config_reader, simulator_factory
    )
    input_dto = make_input_dto()
    with pytest.raises(ApplicationError, match="Invalid data format"):
        use_case.execute(input_dto)


def test_run_single_scenario_invalid_config_data():
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.return_value = [
        WindReading(datetime(2023, 1, 1, 0, 0, 0), 10.0, 0.0)]
    mock_config_reader = MagicMock()
    mock_config_reader.read.side_effect = ValueError("bad config data")
    simulator_factory = MagicMock()
    use_case = RunSingleSimulationScenarioUseCase(
        mock_wind_data_reader, mock_config_reader, simulator_factory
    )
    input_dto = make_input_dto()
    with pytest.raises(ApplicationError, match="Invalid data format"):
        use_case.execute(input_dto)


def test_run_single_scenario_empty_wind_data():
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.return_value = []
    mock_config_reader = MagicMock()
    mock_config_reader.read.return_value = MagicMock(spec=PowerPlantModel)
    simulator_factory = MagicMock()
    use_case = RunSingleSimulationScenarioUseCase(
        mock_wind_data_reader, mock_config_reader, simulator_factory
    )
    input_dto = make_input_dto()
    with pytest.raises(ApplicationError, match="No wind data found"):
        use_case.execute(input_dto)


def test_run_single_scenario_factory_called():
    wind_readings = [WindReading(datetime(2023, 1, 1, 0, 0, 0), 10.0, 0.0)]
    power_plant_model = MagicMock(spec=PowerPlantModel)
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.return_value = wind_readings
    mock_config_reader = MagicMock()
    mock_config_reader.read.return_value = power_plant_model
    mock_simulator = MagicMock()
    simulator_factory = MagicMock(return_value=mock_simulator)
    use_case = RunSingleSimulationScenarioUseCase(
        mock_wind_data_reader, mock_config_reader, simulator_factory
    )
    input_dto = make_input_dto()
    use_case.execute(input_dto)
    simulator_factory.assert_called_once_with(power_plant_model)


def test_run_single_scenario_multiple_power_values():
    wind_readings = [
        WindReading(datetime(2023, 1, 1, 0, 0, 0), 10.0, 0.0),
        WindReading(datetime(2023, 1, 1, 0, 10, 0), 12.0, 0.0)
    ]
    power_plant_model = MagicMock(spec=PowerPlantModel)
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.return_value = wind_readings
    mock_config_reader = MagicMock()
    mock_config_reader.read.return_value = power_plant_model
    mock_simulator = MagicMock()
    # 1回目: 500W, 2回目: 1500W
    mock_simulator.calculate_instantaneous_power.side_effect = [
        Power(500.0), Power(1500.0)]
    simulator_factory = MagicMock(return_value=mock_simulator)
    use_case = RunSingleSimulationScenarioUseCase(
        mock_wind_data_reader, mock_config_reader, simulator_factory
    )
    input_dto = make_input_dto()
    output = use_case.execute(input_dto)
    # Δt固定値で2点分
    delta_t_hours = DEFAULT_TIME_INTERVAL_HOURS
    total_energy_wh = 500.0 * delta_t_hours + 1500.0 * delta_t_hours
    expected_kwh = total_energy_wh / 1000.0
    assert output.annual_power_kwh == pytest.approx(expected_kwh)


def test_run_single_scenario_unexpected_exception():
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.side_effect = OSError("disk error")
    mock_config_reader = MagicMock()
    simulator_factory = MagicMock()
    use_case = RunSingleSimulationScenarioUseCase(
        mock_wind_data_reader, mock_config_reader, simulator_factory
    )
    input_dto = make_input_dto()
    with pytest.raises(ApplicationError, match="Unexpected error: disk error"):
        use_case.execute(input_dto)
