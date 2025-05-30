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
        """
        Args:
            wind_data_reader: 風況データを読み込むためのリポジトリインターフェース
            power_plant_model_reader: 設備特性モデルを読み込むためのリポジトリインターフェース
            power_generation_simulator_factory: PowerPlantModel -> PowerGenerationSimulator を返すファクトリ
        """
        self._wind_data_reader = wind_data_reader
        self._power_plant_model_reader = power_plant_model_reader
        self._power_generation_simulator_factory = power_generation_simulator_factory

    def execute(self, input_dto: SingleScenarioInputDTO) -> SingleScenarioOutputDTO:
        """
        シナリオを実行し、年間発電量(kWh)を計算する。
        Args:
            input_dto: シナリオ入力DTO
        Returns:
            SingleScenarioOutputDTO: 年間発電量(kWh)
        Raises:
            ApplicationError: 入力ファイルが見つからない/データ不正/風況データ空など
        """
        try:
            wind_readings = list(self._wind_data_reader.read(
                input_dto.wind_data_file_path))
            if not wind_readings:
                raise ValueError("No wind data found or file is empty.")
            power_plant_model = self._power_plant_model_reader.read(
                input_dto.config_file_path)
        except FileNotFoundError as e:
            raise ApplicationError(
                f"Input file not found: {e.filename}") from e
        except ValueError as e:
            raise ApplicationError(f"Invalid data format: {e}") from e
        except Exception as e:
            raise ApplicationError(f"Unexpected error: {e}") from e

        simulator = self._power_generation_simulator_factory(power_plant_model)
        # 10分間隔データ前提（プロジェクト定義より）
        time_interval_hours = DEFAULT_TIME_INTERVAL_HOURS
        total_power_w_hours = 0.0
        for reading in wind_readings:
            instantaneous_power_w = simulator.calculate_instantaneous_power(
                wind_reading=reading,
                turbine_angle_deg=input_dto.turbine_angle_deg,
                efficiency=input_dto.efficiency,
                voltage=input_dto.voltage,
                cut_in_rpm=input_dto.cut_in_rpm
            )
            # 各時刻の瞬時電力[W] × 時間間隔[h] を積算
            total_power_w_hours += instantaneous_power_w.value * time_interval_hours
        annual_kwh = total_power_w_hours / 1000.0
        return SingleScenarioOutputDTO(annual_power_generation_kwh=annual_kwh)
