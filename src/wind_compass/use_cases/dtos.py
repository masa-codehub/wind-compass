from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MultipleScenariosInputDTO:
    wind_data_path: str
    config_file_path: str
    angles: List[float]
    efficiency: Optional[float] = None
    voltage: Optional[float] = None
    cut_in_rpm: Optional[float] = None


@dataclass
class ScenarioResult:
    angle: float
    annual_power: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class SingleScenarioInputDTO:
    wind_data_path: str
    config_file_path: str
    angle: float
    efficiency: Optional[float] = None
    voltage: Optional[float] = None
    cut_in_rpm: Optional[float] = None


@dataclass
class SingleScenarioOutputDTO:
    annual_power: Optional[float] = None
    error_message: Optional[str] = None
