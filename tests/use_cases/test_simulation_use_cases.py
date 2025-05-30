from wind_compass.use_cases.simulation_use_cases import RunMultipleSimulationScenariosUseCase
from wind_compass.use_cases.dtos import MultipleScenariosInputDTO, ScenarioResult
import pytest
from unittest.mock import Mock


class DummyInputDTO:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_multiple_scenarios_success():
    mock_single = Mock()
    # モックは入力の角度で異なる値を返す

    def fake_execute(single_input):
        angle = getattr(single_input, 'angle', 0)
        return type('Result', (), {'annual_power': angle * 10})()
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
    assert results[0].annual_power == 0 * 10
    assert results[1].annual_power == 90 * 10


def test_multiple_scenarios_with_error():
    mock_single = Mock()

    def fake_execute(single_input):
        angle = getattr(single_input, 'angle', 0)
        if angle == 90:
            raise ValueError('test error')
        return type('Result', (), {'annual_power': 123})()
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
    assert results[0].annual_power == 123
    assert results[1].error_message is not None
