from typing import List
from .dtos import MultipleScenariosInputDTO, ScenarioResult, SingleScenarioInputDTO
from wind_compass.use_cases.run_single_scenario import RunSingleSimulationScenarioUseCase, ApplicationError


class RunMultipleSimulationScenariosUseCase:
    def __init__(self, single_scenario_use_case: RunSingleSimulationScenarioUseCase):
        self._single_scenario_use_case = single_scenario_use_case

    def execute(self, input_dto: MultipleScenariosInputDTO) -> List[ScenarioResult]:
        results = []
        for angle in input_dto.angles:
            single_input = SingleScenarioInputDTO(
                wind_data_path=input_dto.wind_data_path,
                config_file_path=input_dto.config_file_path,
                angle=angle,
                efficiency=input_dto.efficiency,
                voltage=input_dto.voltage,
                cut_in_rpm=input_dto.cut_in_rpm,
            )
            try:
                output = self._single_scenario_use_case.execute(single_input)
                results.append(ScenarioResult(
                    angle=angle,
                    annual_power_kwh=output.annual_power_kwh,
                    error_message=output.error_message
                ))
            except ApplicationError as e:
                results.append(ScenarioResult(
                    angle=angle,
                    annual_power_kwh=None,
                    error_message=str(e)
                ))
            except Exception as e:
                results.append(ScenarioResult(
                    angle=angle,
                    annual_power_kwh=None,
                    error_message=str(e)
                ))
        return results
