import os
import pytest
from datetime import datetime
from wind_compass.use_cases.run_single_scenario import RunSingleSimulationScenarioUseCase
from wind_compass.use_cases.dtos import SingleScenarioInputDTO
from wind_compass.adapters.data_readers import CsvWindDataReader, JsonConfigReader
from wind_compass.domain.services import PowerGenerationSimulator

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), '../fixtures')


def make_input_dto(config_file_name):
    return SingleScenarioInputDTO(
        wind_data_file_path=os.path.join(FIXTURES_DIR, 'valid_wind_data.csv'),
        config_file_path=os.path.join(FIXTURES_DIR, config_file_name),
        turbine_angle_deg=0.0,
        efficiency=0.9,
        voltage=100.0,
        cut_in_rpm=10.0
    )


def make_input_dto_with_wind(config_file_name, wind_file_name):
    return SingleScenarioInputDTO(
        wind_data_file_path=os.path.join(FIXTURES_DIR, wind_file_name),
        config_file_path=os.path.join(FIXTURES_DIR, config_file_name),
        turbine_angle_deg=0.0,
        efficiency=0.9,
        voltage=100.0,
        cut_in_rpm=10.0
    )


def test_annual_power_generation_differs_between_configs():
    """
    通常の風況データ（valid_wind_data.csv）は有効風速やカットイン条件により発電量が0になるため、
    このテストは設備特性の差分検証には適さない。強風データのテストのみを残す。
    """
    pytest.skip("通常の風況データでは発電量が0となるため、このテストはスキップします。設備特性比較は強風データで検証済み。")


def test_annual_power_generation_differs_between_configs_strong_wind():
    wind_data_reader = CsvWindDataReader()
    config_reader = JsonConfigReader()
    def simulator_factory(model): return PowerGenerationSimulator(model)
    use_case = RunSingleSimulationScenarioUseCase(
        wind_data_reader, config_reader, simulator_factory
    )
    input_dto_a = make_input_dto_with_wind(
        'valid_config.json', 'valid_wind_data_strong.csv')
    input_dto_b = make_input_dto_with_wind(
        'valid_config_B.json', 'valid_wind_data_strong.csv')
    output_a = use_case.execute(input_dto_a)
    output_b = use_case.execute(input_dto_b)
    assert output_a.annual_power_generation_kwh != output_b.annual_power_generation_kwh
    assert output_a.annual_power_generation_kwh > 0
    assert output_b.annual_power_generation_kwh > 0
