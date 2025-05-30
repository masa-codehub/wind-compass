import json
import pandas as pd
from typing import Iterable
from datetime import datetime
from wind_compass.domain.models import WindReading, PowerPlantModel, PolynomialCurve
from wind_compass.use_cases.ports import WindDataReader, PowerPlantModelReader


class CsvWindDataReader(WindDataReader):
    def read(self, file_path: str) -> Iterable[WindReading]:
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            raise
        except pd.errors.ParserError as e:
            raise ValueError(f"Failed to parse CSV file: {e}")
        required_cols = ["observed_at",
                         "max_wind_speed_mps", "max_wind_direction_deg"]
        if not all(col in df.columns for col in required_cols):
            raise ValueError("CSV missing required columns")
        try:
            df['observed_at'] = pd.to_datetime(df['observed_at'])
            df['max_wind_speed_mps'] = df['max_wind_speed_mps'].astype(float)
            df['max_wind_direction_deg'] = df['max_wind_direction_deg'].astype(
                float)
            readings = [
                WindReading(
                    observed_at=row.observed_at,
                    wind_speed=row.max_wind_speed_mps,
                    wind_direction=row.max_wind_direction_deg
                ) for row in df.itertuples(index=False)
            ]
            return readings
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid data type in CSV columns: {e}")


class JsonConfigReader(PowerPlantModelReader):
    TURBINE_POWER_CURVE = "turbine_power_curve"
    GENERATOR_TORQUE_CURVE = "generator_torque_curve"
    GENERATOR_CURRENT_CURVE = "generator_current_curve"
    COEFFS = "coeffs"

    def read(self, file_path: str) -> PowerPlantModel:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise
        except json.JSONDecodeError as e:
            raise
        except OSError as e:
            raise ValueError(f"Failed to read JSON file: {e}")
        try:
            t_curve = PolynomialCurve(coeffs=list(
                data[self.TURBINE_POWER_CURVE][self.COEFFS]))
            g_torque = PolynomialCurve(coeffs=list(
                data[self.GENERATOR_TORQUE_CURVE][self.COEFFS]))
            g_current = PolynomialCurve(coeffs=list(
                data[self.GENERATOR_CURRENT_CURVE][self.COEFFS]))
        except KeyError as e:
            raise ValueError(f"Missing key in config: {e}")
        except Exception as e:
            raise ValueError(f"Invalid config data: {e}")
        return PowerPlantModel(
            power_curve=t_curve,
            torque_curve=g_torque,
            current_curve=g_current
        )


__all__ = ["CsvWindDataReader", "JsonConfigReader"]
