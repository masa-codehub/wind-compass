from dataclasses import dataclass


@dataclass(frozen=True)
class SingleScenarioInputDTO:
    """
    単一シナリオ実行の入力DTO。
    Args:
        wind_data_file_path: 風況データCSVファイルのパス
        config_file_path: 設備モデル設定ファイルのパス
        turbine_angle_deg: タービン角度（度）
        efficiency: 発電効率（0.0-1.0）
        voltage: 発電機出力電圧（V）
        cut_in_rpm: カットイン回転数（rpm）
    """
    wind_data_file_path: str
    config_file_path: str
    turbine_angle_deg: float
    efficiency: float
    voltage: float
    cut_in_rpm: float


@dataclass(frozen=True)
class SingleScenarioOutputDTO:
    annual_power_generation_kwh: float
