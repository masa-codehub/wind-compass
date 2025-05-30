from wind_compass.adapters.data_readers import CsvWindDataReader, JsonConfigReader
from wind_compass.domain.models import WindReading, PowerPlantModel
import os
import pytest

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), '../fixtures')


class TestCsvWindDataReader:
    def test_read_valid_csv_returns_wind_readings(self):
        reader = CsvWindDataReader()
        file_path = os.path.join(FIXTURES_DIR, 'valid_wind_data.csv')
        readings = list(reader.read(file_path))
        assert len(readings) == 2
        assert isinstance(readings[0], WindReading)
        assert readings[0].wind_speed == 5.0 # Updated to match the actual content of valid_wind_data.csv
        assert readings[0].wind_direction == 0.0 # Updated to match the actual content of valid_wind_data.csv

    def test_read_non_existent_csv_raises_file_not_found_error(self):
        reader = CsvWindDataReader()
        file_path = os.path.join(FIXTURES_DIR, 'not_exist.csv')
        with pytest.raises(FileNotFoundError):
            list(reader.read(file_path))

    def test_read_csv_with_missing_columns_raises_value_error(self):
        reader = CsvWindDataReader()
        file_path = os.path.join(
            FIXTURES_DIR, 'invalid_wind_data_missing_column.csv')
        with pytest.raises(ValueError):
            list(reader.read(file_path))

    def test_read_csv_with_bad_data_type_raises_value_error(self):
        reader = CsvWindDataReader()
        file_path = os.path.join(
            FIXTURES_DIR, 'invalid_wind_data_bad_type.csv')
        with pytest.raises(ValueError):
            list(reader.read(file_path))


class TestJsonConfigReader:
    def test_read_valid_json_returns_power_plant_model(self):
        reader = JsonConfigReader()
        file_path = os.path.join(FIXTURES_DIR, 'valid_config.json')
        model = reader.read(file_path)
        assert isinstance(model, PowerPlantModel)
        assert model.power_curve.coeffs == [0.0, 1.0, 2.0, 3.0]
        assert model.torque_curve.coeffs == [0.1, 1.1, 2.1, 3.1]
        assert model.current_curve.coeffs == [0.2, 1.2, 2.2, 3.2]

    def test_read_non_existent_json_raises_file_not_found_error(self):
        reader = JsonConfigReader()
        file_path = os.path.join(FIXTURES_DIR, 'not_exist.json')
        with pytest.raises(FileNotFoundError):
            reader.read(file_path)

    def test_read_json_with_missing_key_raises_value_error(self):
        reader = JsonConfigReader()
        file_path = os.path.join(
            FIXTURES_DIR, 'invalid_config_missing_key.json')
        with pytest.raises(ValueError):
            reader.read(file_path)

    def test_read_json_with_wrong_coeffs_count_raises_value_error(self):
        reader = JsonConfigReader()
        file_path = os.path.join(
            FIXTURES_DIR, 'invalid_config_wrong_coeffs_count.json')
        with pytest.raises(ValueError):
            reader.read(file_path)

    def test_read_json_with_bad_json_raises_json_decode_error(self):
        import json
        reader = JsonConfigReader()
        file_path = os.path.join(FIXTURES_DIR, 'invalid_config_bad_json.json')
        with pytest.raises(json.JSONDecodeError):
            reader.read(file_path)