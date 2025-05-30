from typing import List, Optional, Callable
import logging
from .dtos import MultipleScenariosInputDTO, ScenarioResult, SingleScenarioInputDTO, SingleScenarioOutputDTO
from wind_compass.domain.models import PowerPlantModel, Power, WindReading
from wind_compass.use_cases.ports import WindDataReader
# Assuming ApplicationError might be raised by the chosen single_scenario_use_case
# If the single_scenario_use_case is the one defined in this file, it doesn't raise ApplicationError directly in its execute method's happy path
# but RunMultipleSimulationScenariosUseCase might be used with other implementations.
# For now, let's import it if it's intended to be caught.
# from wind_compass.use_cases.run_single_scenario import ApplicationError # This line depends on which single_scenario_use_case is used


class RunSingleSimulationScenarioUseCase:
    input_dto_class = SingleScenarioInputDTO
    output_dto_class = SingleScenarioOutputDTO

    def __init__(self, simulator_factory: Callable[[PowerPlantModel], object], model_loader: Callable[[str], PowerPlantModel], wind_data_reader: WindDataReader):
        self.simulator_factory = simulator_factory  # model→simulatorインスタンス
        self.model_loader = model_loader
        self.wind_data_reader = wind_data_reader

    def execute(self, input_dto: SingleScenarioInputDTO) -> SingleScenarioOutputDTO:
        """
        年間発電量計算: 風況データN件→N-1区間のΔtを推定し、各区間の始点の瞬時電力×Δtで積算。
        データ0件・1件は0kWh。瞬時発電量計算エラー時は0W、Δt<=0も0h扱い。
        """
        try:
            model = self.model_loader(input_dto.config_file_path)
            wind_data = self.wind_data_reader.read(input_dto.wind_data_path)
            if not wind_data:
                return SingleScenarioOutputDTO(annual_power_kwh=0.0)
            if len(wind_data) == 1:
                return SingleScenarioOutputDTO(annual_power_kwh=0.0)
            simulator = self.simulator_factory(model)
            total_energy_wh = 0.0
            for i in range(len(wind_data) - 1):
                w = wind_data[i]
                next_w = wind_data[i + 1]
                try:
                    p = simulator.calculate_instantaneous_power(
                        w,
                        input_dto.angle,
                        input_dto.efficiency if input_dto.efficiency is not None else 1.0,
                        input_dto.voltage if input_dto.voltage is not None else 100.0,
                        input_dto.cut_in_rpm if input_dto.cut_in_rpm is not None else 0.0,
                    )
                except Exception as ex:
                    logging.warning(
                        f"Instantaneous power calculation failed: {ex}")
                    p = Power(0.0)
                interval_seconds = (next_w.observed_at -
                                    w.observed_at).total_seconds()
                delta_t_hours = max(interval_seconds / 3600.0, 0.0)
                total_energy_wh += p.value * delta_t_hours
            annual_power_kwh = total_energy_wh / 1000.0
            return SingleScenarioOutputDTO(annual_power_kwh=annual_power_kwh)
        except Exception as e:
            return SingleScenarioOutputDTO(annual_power_kwh=None, error_message=str(e))


class RunMultipleSimulationScenariosUseCase:
    # The type hint for single_scenario_use_case should ideally be the specific class
    # or an Abstract Base Class / Protocol if multiple implementations are possible.
    # For now, using the class defined above.
    def __init__(self, single_scenario_use_case: RunSingleSimulationScenarioUseCase):
        self._single_scenario_use_case = single_scenario_use_case

    def execute(self, input_dto: MultipleScenariosInputDTO) -> List[ScenarioResult]:
        results = []
        for angle in input_dto.angles:
            # Assuming single_scenario_use_case has input_dto_class attribute
            # If not, SingleScenarioInputDTO should be used directly.
            # The `issue#37_01` version of RunSingleSimulationScenarioUseCase has this attribute.
            single_input = self._single_scenario_use_case.input_dto_class(
                wind_data_path=input_dto.wind_data_path,
                config_file_path=input_dto.config_file_path,
                angle=angle,
                efficiency=input_dto.efficiency,
                voltage=input_dto.voltage,
                cut_in_rpm=input_dto.cut_in_rpm,
            )
            try:
                output = self._single_scenario_use_case.execute(single_input)
                # Adopted from 'main' branch for more complete ScenarioResult
                results.append(ScenarioResult(
                    angle=angle,
                    # Assuming output DTO always has these attributes, might be None
                    annual_power_kwh=output.annual_power_kwh,
                    error_message=output.error_message
                ))
            # Catching ApplicationError specifically if single_scenario_use_case can raise it
            # and it needs different handling than a generic Exception.
            # If single_scenario_use_case is the one in this file, it wraps all its own exceptions
            # into SingleScenarioOutputDTO(error_message=...).
            # So, ApplicationError might not be directly thrown by *this* execute unless the injected
            # single_scenario_use_case is a different implementation (e.g., from run_single_scenario.py)
            # except ApplicationError as e: # Retaining this block from 'main' for robustness with other use case impls
            #     results.append(ScenarioResult(
            #         angle=angle,
            #         annual_power_kwh=None,
            #         error_message=str(e)
            #     ))
            except Exception as e: # Generic exception handler
                results.append(ScenarioResult(
                    angle=angle,
                    annual_power_kwh=None,
                    error_message=str(e)
                ))
        return results