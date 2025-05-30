from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class SingleScenarioInputDTO:
    """
    Input DTO for a single simulation scenario.

    Args:
        wind_data_path: Path to the wind data CSV file.
        config_file_path: Path to the power plant model JSON config file.
        angle: Turbine angle in degrees.
        efficiency: Overall efficiency (e.g., 0.85 for 85%). Defaults to None.
        voltage: Generator terminal voltage (V). Defaults to None.
        cut_in_rpm: Generator cut-in RPM. Defaults to None.
    """
    wind_data_path: str
    config_file_path: str
    angle: float # Matches current use_cases/simulation_use_cases.py and cli.py for input
    efficiency: Optional[float] = None
    voltage: Optional[float] = None
    cut_in_rpm: Optional[float] = None

@dataclass(frozen=True)
class SingleScenarioOutputDTO:
    """
    Output DTO for a single simulation scenario.

    Args:
        annual_power_kwh: Calculated annual power generation in kWh. Optional if an error occurred.
        error_message: Error message if the simulation for this scenario failed. Optional.
    """
    annual_power_kwh: Optional[float] = None
    error_message: Optional[str] = None

@dataclass(frozen=True)
class MultipleScenariosInputDTO:
    """
    Input DTO for running multiple simulation scenarios.

    Args:
        wind_data_path: Path to the wind data CSV file.
        config_file_path: Path to the power plant model JSON config file.
        angles: List of turbine angles in degrees to simulate.
        efficiency: Overall efficiency (e.g., 0.85 for 85%). Applied to all scenarios if provided. Defaults to None.
        voltage: Generator terminal voltage (V). Applied to all scenarios if provided. Defaults to None.
        cut_in_rpm: Generator cut-in RPM. Applied to all scenarios if provided. Defaults to None.
    """
    wind_data_path: str
    config_file_path: str
    angles: List[float]
    efficiency: Optional[float] = None
    voltage: Optional[float] = None
    cut_in_rpm: Optional[float] = None

@dataclass(frozen=True)
class ScenarioResult:
    """
    Represents the result of a single scenario within a multiple scenario execution.

    Args:
        angle: The turbine angle for this scenario.
        annual_power_kwh: Calculated annual power generation in kWh for this scenario. Optional if an error occurred.
        error_message: Error message if the simulation for this scenario failed. Optional.
    """
    angle: float
    annual_power_kwh: Optional[float] = None # Renamed from annual_power for consistency
    error_message: Optional[str] = None