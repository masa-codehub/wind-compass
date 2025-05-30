from typing import List, Optional, Any
import logging
from .dtos import MultipleScenariosInputDTO, ScenarioResult, SingleScenarioInputDTO, SingleScenarioOutputDTO


class RunSingleSimulationScenarioUseCase:
    input_dto_class = SingleScenarioInputDTO
    output_dto_class = SingleScenarioOutputDTO

    def __init__(self, simulator_factory, model_loader, wind_data_reader):
        self.simulator_factory = simulator_factory  # model→simulatorインスタンス
        self.model_loader = model_loader
        self.wind_data_reader = wind_data_reader

    def execute(self, input_dto: SingleScenarioInputDTO) -> SingleScenarioOutputDTO:
        try:
            model = self.model_loader(input_dto.config_file_path)
            wind_data = self.wind_data_reader.read(input_dto.wind_data_path)
            total_power = 0.0
            error_count = 0
            for w in wind_data:
                try:
                    p = self.simulator_factory(model).calculate_instantaneous_power(
                        w,
                        input_dto.angle,
                        input_dto.efficiency if input_dto.efficiency is not None else 1.0,
                        input_dto.voltage if input_dto.voltage is not None else 100.0,
                        input_dto.cut_in_rpm if input_dto.cut_in_rpm is not None else 0.0,
                    )
                    total_power += p.value
                except Exception as ex:
                    logging.warning(
                        f"Instantaneous power calculation failed: {ex}")
                    error_count += 1
                    total_power += 0.0
            # Δt（時間間隔）をwind_dataのobserved_atから推定
            if len(wind_data) >= 2:
                interval_seconds = (
                    wind_data[1].observed_at - wind_data[0].observed_at).total_seconds()
                delta_t = interval_seconds / 3600.0
            elif len(wind_data) == 1:
                delta_t = 1.0
            else:
                delta_t = 0.0
            annual_power_kwh = (total_power * delta_t) / 1000
            return SingleScenarioOutputDTO(annual_power=annual_power_kwh)
        except Exception as e:
            return SingleScenarioOutputDTO(annual_power=None, error_message=str(e))


class RunMultipleSimulationScenariosUseCase:
    def __init__(self, single_scenario_use_case: Any):
        self._single_scenario_use_case = single_scenario_use_case

    def execute(self, input_dto: MultipleScenariosInputDTO) -> List[ScenarioResult]:
        results = []
        for angle in input_dto.angles:
            try:
                single_input = self._single_scenario_use_case.input_dto_class(
                    wind_data_path=input_dto.wind_data_path,
                    config_file_path=input_dto.config_file_path,
                    angle=angle,
                    efficiency=input_dto.efficiency,
                    voltage=input_dto.voltage,
                    cut_in_rpm=input_dto.cut_in_rpm,
                )
                output = self._single_scenario_use_case.execute(single_input)
                annual_power = getattr(output, 'annual_power', None)
                results.append(ScenarioResult(
                    angle=angle, annual_power=annual_power))
            except Exception as e:
                results.append(ScenarioResult(
                    angle=angle, error_message=str(e)))
        return results
