from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class WindReading:
    """ある時刻の風況観測データを表す値オブジェクト"""
    observed_at: datetime
    wind_speed: float  # max_wind_speed_mps
    wind_direction: float  # max_wind_direction_deg


@dataclass(frozen=True)
class PolynomialCurve:
    """3次多項式カーブの係数を保持する値オブジェクト"""
    coeffs: List[float]

    def __post_init__(self):
        if len(self.coeffs) != 4:
            raise ValueError("PolynomialCurve must have 4 coefficients.")


@dataclass(frozen=True)
class PowerPlantModel:
    """設備特性のモデルを保持するエンティティ"""
    turbine_power_curve: PolynomialCurve
    generator_torque_curve: PolynomialCurve
    generator_current_curve: PolynomialCurve
