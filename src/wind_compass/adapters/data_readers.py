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
    EXPECTED_COEFFS_COUNT = 4

    def _validate_curve_data(self, curve_data: dict, curve_name: str):
        if self.COEFFS not in curve_data:
            raise ValueError(
                f"Missing key '{self.COEFFS}' in '{curve_name}' config.")
        coeffs = curve_data[self.COEFFS]
        if not isinstance(coeffs, list):
            raise ValueError(
                f"'{self.COEFFS}' in '{curve_name}' must be a list.")
        if len(coeffs) != self.EXPECTED_COEFFS_COUNT:
            raise ValueError(
                f"'{self.COEFFS}' in '{curve_name}' must have exactly {self.EXPECTED_COEFFS_COUNT} elements."
            )
        if not all(isinstance(c, (int, float)) for c in coeffs):
            raise ValueError(
                f"All elements in '{self.COEFFS}' in '{curve_name}' must be numbers."
            )

    def read(self, file_path: str) -> PowerPlantModel:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise
        except json.JSONDecodeError as e:
            # Add file_path to the error message for better context
            raise json.JSONDecodeError(f"Failed to decode JSON from {file_path}: {e.msg}", e.doc, e.pos)
        except OSError as e:
            raise ValueError(f"Failed to read JSON file {file_path}: {e}")

        required_top_keys = [
            self.TURBINE_POWER_CURVE,
            self.GENERATOR_TORQUE_CURVE,
            self.GENERATOR_CURRENT_CURVE
        ]
        for key in required_top_keys:
            if key not in data:
                raise ValueError(
                    f"Missing top-level key '{key}' in config file: {file_path}")
            if not isinstance(data[key], dict):
                raise ValueError(
                    f"Top-level key '{key}' in config file {file_path} must be a dictionary."
                )

        try:
            self._validate_curve_data(
                data[self.TURBINE_POWER_CURVE], self.TURBINE_POWER_CURVE)
            t_curve = PolynomialCurve(coeffs=list(
                data[self.TURBINE_POWER_CURVE][self.COEFFS]))

            self._validate_curve_data(
                data[self.GENERATOR_TORQUE_CURVE], self.GENERATOR_TORQUE_CURVE)
            g_torque = PolynomialCurve(coeffs=list(
                data[self.GENERATOR_TORQUE_CURVE][self.COEFFS]))

            self._validate_curve_data(
                data[self.GENERATOR_CURRENT_CURVE], self.GENERATOR_CURRENT_CURVE)
            g_current = PolynomialCurve(coeffs=list(
                data[self.GENERATOR_CURRENT_CURVE][self.COEFFS]))
        
        # Catch ValueError from _validate_curve_data or PolynomialCurve init
        # KeyError should be caught by the top-level key check or _validate_curve_data
        except (ValueError, TypeError) as e: 
            raise ValueError(f"Invalid config data in {file_path}: {e}") from e
        except Exception as e: # Catch any other unexpected errors
            raise ValueError(
                f"Unexpected error processing config data in {file_path}: {e}") from e

        return PowerPlantModel(
            power_curve=t_curve,
            torque_curve=g_torque,
            current_curve=g_current
        )


__all__ = ["CsvWindDataReader", "JsonConfigReader"]