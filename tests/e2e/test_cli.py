import sys
import os
import subprocess
import tempfile
import shutil
import pytest


def test_cli_matrix_output():
    wind_path = os.path.join(os.path.dirname(
        __file__), '../fixtures/valid_wind_data.csv')
    config_path = os.path.join(os.path.dirname(
        __file__), '../fixtures/valid_config.json')
    cmd = [sys.executable, "main.py", "--wind-data", wind_path,
           "--config-file", config_path, "--angles", "0,90"]
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/../../')
    assert result.returncode == 0
    out = result.stdout
    assert "Angle (deg)" in out
    assert "Annual Power" in out
    # 期待値は角度ごとのみ
    assert "0" in out
    assert "90" in out


def test_cli_help():
    cmd = [sys.executable, "main.py", "--help"]
    result = subprocess.run(cmd, capture_output=True,
                            text=True, cwd=os.path.dirname(__file__) + '/../../')
    assert result.returncode == 0
    assert "--wind-data" in result.stdout
    assert "--angles" in result.stdout
