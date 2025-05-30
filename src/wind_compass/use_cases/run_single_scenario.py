from typing import Callable
from wind_compass.use_cases.ports import WindDataReader, PowerPlantModelReader
from wind_compass.domain.services import PowerGenerationSimulator
from wind_compass.use_cases.dtos import SingleScenarioInputDTO, SingleScenarioOutputDTO
from wind_compass.domain.constants import DEFAULT_TIME_INTERVAL_HOURS


class ApplicationError(Exception):
    """アプリケーション層の例外。ユースケース内で発生したエラーをラップする。"""
    pass


class RunSingleSimulationScenarioUseCase:
    """
    単一のシミュレーションシナリオを実行し、年間発電量を計算するユースケース。
    依存性注入によりリーダ・ファクトリを受け取る。
    """

    def __init__(self,
                 wind_data_reader: WindDataReader,
                 power_plant_model_reader: PowerPlantModelReader,
                 power_generation_simulator_factory: Callable[[object], PowerGenerationSimulator]):
        self._wind_data_reader = wind_data_reader
        self._power_plant_model_reader = power_plant_model_reader
        self._power_generation_simulator_factory = power_generation_simulator_factory

    def execute(self, input_dto: SingleScenarioInputDTO) -> SingleScenarioOutputDTO:
        try:
            wind_readings = list(
                self._wind_data_reader.read(input_dto.wind_data_path))
            if not wind_readings:
                raise ValueError("No wind data found or file is empty.")
            power_plant_model = self._power_plant_model_reader.read(
                input_dto.config_file_path)
        except FileNotFoundError as e:
            raise ApplicationError(
                f"Input file not found: {e.filename if hasattr(e, 'filename') else str(e)}") from e
        except ValueError as e:
            raise ApplicationError(f"Invalid data format: {e}") from e
        except Exception as e:
            raise ApplicationError(f"Unexpected error: {e}") from e

        simulator = self._power_generation_simulator_factory(power_plant_model)
        total_power = 0.0
        for reading in wind_readings:
            try:
                p = simulator.calculate_instantaneous_power(
                    wind_reading=reading,
                    turbine_angle_deg=input_dto.angle,
                    efficiency=input_dto.efficiency,
                    voltage=input_dto.voltage,
                    cut_in_rpm=input_dto.cut_in_rpm
                )
                total_power += p.value
            except Exception as ex:
                # 1点失敗しても他は継続
                total_power += 0.0
        # Δtはプロジェクト定義の固定値（10分=1/6h）
        delta_t = DEFAULT_TIME_INTERVAL_HOURS
        annual_power_kwh = (total_power * delta_t) / 1000.0
        return SingleScenarioOutputDTO(annual_power_kwh=annual_power_kwh)
