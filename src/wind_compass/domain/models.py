from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass(frozen=True)
class Power:
    """電力を表す値オブジェクト (単位: W)"""
    value: float

    def __add__(self, other: 'Power') -> 'Power':
        if not isinstance(other, Power):
            return NotImplemented
        return Power(self.value + other.value)

    def __sub__(self, other: 'Power') -> 'Power':
        if not isinstance(other, Power):
            return NotImplemented
        return Power(self.value - other.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Power):
            return False
        return self.value == other.value


@dataclass(frozen=True)
class Energy:
    """エネルギーを表す値オブジェクト (単位: J)"""
    value: float

    def __add__(self, other: 'Energy') -> 'Energy':
        if not isinstance(other, Energy):
            return NotImplemented
        return Energy(self.value + other.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Energy):
            return False
        return self.value == other.value


@dataclass(frozen=True)
class Torque:
    """トルクを表す値オブジェクト (単位: Nm)"""
    value: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Torque):
            return False
        return self.value == other.value


@dataclass(frozen=True)
class EffectiveWindSpeed:
    """有効風速を表す値オブジェクト (単位: m/s)"""
    value: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EffectiveWindSpeed):
            return False
        return self.value == other.value


@dataclass(frozen=True)
class WindReading:
    """観測時刻・風速・風向を表す値オブジェクト"""
    observed_at: datetime
    wind_speed: float  # m/s (mainブランチのコメント: max_wind_speed_mps を考慮し、m/s と明記)
    # deg (mainブランチのコメント: max_wind_direction_deg を考慮し、deg と明記)
    wind_direction: float


@dataclass(frozen=True)
class PolynomialCurve:
    """多項式カーブを表す。coeffs: [cN, ..., c0] 降べき順"""
    coeffs: List[float]

    def __post_init__(self):
        if not isinstance(self.coeffs, list):
            raise TypeError("coeffs must be a list of float")
        if not all(isinstance(c, (int, float)) for c in self.coeffs):
            raise TypeError("All coeffs must be float or int")
        # mainブランチの制約(len(self.coeffs) != 4)は、より汎用的なこちらの定義では削除。
        # 必要であれば、このクラスを利用する側で係数の数をチェックする。
        if len(self.coeffs) == 0:
            raise ValueError("coeffs must not be empty")

    def calculate(self, x: float) -> float:
        return sum(c * (x ** i) for i, c in enumerate(reversed(self.coeffs)))


@dataclass(frozen=True)
class PowerPlantModel:
    """設備特性を表す値オブジェクト"""
    power_curve: PolynomialCurve      # 風速(m/s) -> 電力(W)
    torque_curve: PolynomialCurve     # 回転数(krpm) -> トルク(Nm)
    current_curve: PolynomialCurve    # 回転数(krpm) -> 電流(A)

    def __post_init__(self):
        if not all(isinstance(c, PolynomialCurve) for c in [self.power_curve, self.torque_curve, self.current_curve]):
            raise TypeError("All curves must be PolynomialCurve")
