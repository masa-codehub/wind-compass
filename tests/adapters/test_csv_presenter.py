import csv
import pytest
from wind_compass.adapters.csv_presenter import CsvPresenter, PresenterError


def test_csv_presenter_writes_correct_csv(tmp_path):
    matrix_data = {
        'Angle 0': {'Gear 3': 100, 'Gear 5': 200},
        'Angle 22.5': {'Gear 3': 150, 'Gear 5': 250}
    }
    row_labels = ['Angle 0', 'Angle 22.5']
    col_labels = ['Gear 3', 'Gear 5']
    expected = [
        ['', 'Gear 3', 'Gear 5'],
        ['Angle 0', 100, 200],
        ['Angle 22.5', 150, 250]
    ]
    output_file = tmp_path / "report.csv"
    presenter = CsvPresenter(filepath=str(output_file))
    presenter.present(matrix_data, row_labels, col_labels)
    with open(output_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert rows == [[str(cell) for cell in row] for row in expected]


def test_csv_presenter_empty_matrix(tmp_path):
    matrix_data = {}
    row_labels = []
    col_labels = []
    output_file = tmp_path / "empty.csv"
    presenter = CsvPresenter(filepath=str(output_file))
    presenter.present(matrix_data, row_labels, col_labels)
    with open(output_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert rows == [['']]


def test_csv_presenter_invalid_path():
    with pytest.raises(ValueError):
        CsvPresenter(filepath=None)


def test_csv_presenter_ioerror(monkeypatch, tmp_path):
    matrix_data = {'A': {'B': 1}}
    row_labels = ['A']
    col_labels = ['B']
    output_file = tmp_path / "fail.csv"

    def raise_ioerror(*a, **k):
        raise IOError("disk full")

    monkeypatch.setattr("builtins.open", raise_ioerror)
    presenter = CsvPresenter(filepath=str(output_file))
    with pytest.raises(PresenterError):
        presenter.present(matrix_data, row_labels, col_labels)
