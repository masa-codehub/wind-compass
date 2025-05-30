from wind_compass.use_cases.simulation_use_cases import RunMultipleSimulationScenariosUseCase
from wind_compass.use_cases.dtos import MultipleScenariosInputDTO, ScenarioResult
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from wind_compass.use_cases.simulation_use_cases import RunSingleSimulationScenarioUseCase
from wind_compass.use_cases.dtos import SingleScenarioInputDTO
from wind_compass.domain.models import WindReading, PowerPlantModel, Power


class DummyInputDTO:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_multiple_scenarios_success():
    mock_single = Mock()
    # モックは入力の角度で異なる値を返す

    def fake_execute(single_input):
        angle = getattr(single_input, 'angle', 0)
        return type('Result', (), {'annual_power_kwh': angle * 10})()
    mock_single.execute.side_effect = fake_execute
    mock_single.input_dto_class = DummyInputDTO

    usecase = RunMultipleSimulationScenariosUseCase(mock_single)
    input_dto = MultipleScenariosInputDTO(
        wind_data_path='dummy.csv',
        config_file_path='dummy.json',
        angles=[0, 90],
    )
    results = usecase.execute(input_dto)
    assert len(results) == 2
    assert results[0].annual_power_kwh == 0 * 10
    assert results[1].annual_power_kwh == 90 * 10


def test_multiple_scenarios_with_error():
    mock_single = Mock()

    def fake_execute(single_input):
        angle = getattr(single_input, 'angle', 0)
        if angle == 90:
            raise ValueError('test error')
        return type('Result', (), {'annual_power_kwh': 123})()
    mock_single.execute.side_effect = fake_execute
    mock_single.input_dto_class = DummyInputDTO

    usecase = RunMultipleSimulationScenariosUseCase(mock_single)
    input_dto = MultipleScenariosInputDTO(
        wind_data_path='dummy.csv',
        config_file_path='dummy.json',
        angles=[0, 90],
    )
    results = usecase.execute(input_dto)
    assert len(results) == 2
    assert results[0].annual_power_kwh == 123
    assert results[1].error_message is not None


def make_input_dto():
    return SingleScenarioInputDTO(
        wind_data_path="dummy_wind.csv",
        config_file_path="dummy_config.json",
        angle=0.0,
        efficiency=0.9,
        voltage=100.0,
        cut_in_rpm=10.0
    )


def test_annual_power_kwh_zero_when_no_data():
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.return_value = []
    mock_model_loader = MagicMock()
    simulator_factory = MagicMock()
    use_case = RunSingleSimulationScenarioUseCase(
        simulator_factory, mock_model_loader, mock_wind_data_reader)
    input_dto = make_input_dto()
    output = use_case.execute(input_dto)
    assert output.annual_power_kwh == 0.0


def test_annual_power_kwh_zero_when_single_data():
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.return_value = [
        WindReading(datetime(2023, 1, 1, 0, 0, 0), 10.0, 0.0)
    ]
    mock_model_loader = MagicMock()
    simulator_factory = MagicMock()
    use_case = RunSingleSimulationScenarioUseCase(
        simulator_factory, mock_model_loader, mock_wind_data_reader)
    input_dto = make_input_dto()
    output = use_case.execute(input_dto)
    assert output.annual_power_kwh == 0.0


def test_annual_power_kwh_two_points():
    wind_readings = [
        WindReading(datetime(2023, 1, 1, 0, 0, 0), 10.0, 0.0),
        WindReading(datetime(2023, 1, 1, 0, 10, 0), 12.0, 0.0)
    ]
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.return_value = wind_readings
    mock_model_loader = MagicMock()
    mock_model_loader.return_value = MagicMock(spec=PowerPlantModel)
    mock_simulator = MagicMock()
    # 1回目: 500W
    mock_simulator.calculate_instantaneous_power.side_effect = [Power(500.0)]
    simulator_factory = MagicMock(return_value=mock_simulator)
    use_case = RunSingleSimulationScenarioUseCase(
        simulator_factory, mock_model_loader, mock_wind_data_reader)
    input_dto = make_input_dto()
    output = use_case.execute(input_dto)
    # Δt=10分=1/6h, 500W×1/6h=83.33Wh, kWh=0.0833
    expected_kwh = (500.0 * (1/6)) / 1000.0
    assert output.annual_power_kwh == pytest.approx(expected_kwh)


def test_annual_power_kwh_multiple_points_varied_interval():
    wind_readings = [
        WindReading(datetime(2023, 1, 1, 0, 0, 0), 10.0, 0.0),
        WindReading(datetime(2023, 1, 1, 0, 10, 0), 12.0, 0.0),
        WindReading(datetime(2023, 1, 1, 0, 25, 0), 14.0, 0.0)
    ]
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.return_value = wind_readings
    mock_model_loader = MagicMock()
    mock_model_loader.return_value = MagicMock(spec=PowerPlantModel)
    mock_simulator = MagicMock()
    # 1区間目: 1000W, 2区間目: 2000W
    mock_simulator.calculate_instantaneous_power.side_effect = [
        Power(1000.0), Power(2000.0)]
    simulator_factory = MagicMock(return_value=mock_simulator)
    use_case = RunSingleSimulationScenarioUseCase(
        simulator_factory, mock_model_loader, mock_wind_data_reader)
    input_dto = make_input_dto()
    output = use_case.execute(input_dto)
    # 区間1: Δt=10分=1/6h, 区間2: Δt=15分=0.25h
    expected_kwh = (1000.0 * (1/6) + 2000.0 * 0.25) / 1000.0
    assert output.annual_power_kwh == pytest.approx(expected_kwh)


def test_annual_power_kwh_zero_interval():
    wind_readings = [
        WindReading(datetime(2023, 1, 1, 0, 0, 0), 10.0, 0.0),
        WindReading(datetime(2023, 1, 1, 0, 0, 0), 12.0, 0.0)
    ]
    mock_wind_data_reader = MagicMock()
    mock_wind_data_reader.read.return_value = wind_readings
    mock_model_loader = MagicMock()
    mock_model_loader.return_value = MagicMock(spec=PowerPlantModel)
    mock_simulator = MagicMock()
    mock_simulator.calculate_instantaneous_power.side_effect = [Power(1000.0)]
    simulator_factory = MagicMock(return_value=mock_simulator)
    use_case = RunSingleSimulationScenarioUseCase(
        simulator_factory, mock_model_loader, mock_wind_data_reader)
    input_dto = make_input_dto()
    output = use_case.execute(input_dto)
    # Δt=0区間は発電量0
    assert output.annual_power_kwh == 0.0
