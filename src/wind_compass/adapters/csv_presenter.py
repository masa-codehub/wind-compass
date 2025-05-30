import csv
from typing import List, Dict, Any


class PresenterError(Exception):
    """CSV出力時のエラーを表す例外"""
    pass


class CsvPresenter:
    """
    シミュレーション結果のマトリクス表をCSVファイルに出力するPresenter。
    """

    def __init__(self, filepath: str):
        if not filepath:
            raise ValueError("Filepath for CSV output cannot be empty.")
        self.filepath = filepath

    def present(self, matrix_data: Dict[str, Dict[str, Any]], row_labels: List[str], col_labels: List[str]):
        """
        マトリクスデータをCSVファイルに書き出す。
        Args:
            matrix_data: {行キー: {列キー: 値}} 形式のデータ
            row_labels: CSVの行ヘッダー（最初の列）に使用するラベルのリスト
            col_labels: CSVの列ヘッダー（最初の行）に使用するラベルのリスト (最初のセルは空)
        Raises:
            PresenterError: ファイル書き込みに失敗した場合
        """
        try:
            with open(self.filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                header = [""] + col_labels
                writer.writerow(header)
                for r_label in row_labels:
                    row_to_write = [r_label]
                    for c_label in col_labels:
                        value = matrix_data.get(r_label, {}).get(c_label, "")
                        row_to_write.append(value)
                    writer.writerow(row_to_write)
        except IOError as e:
            message = f"Error: Could not write CSV file to {self.filepath}. Details: {e}"
            print(message)
            raise PresenterError(message) from e
        except Exception as e:
            message = f"An unexpected error occurred while writing CSV: {e}"
            print(message)
            raise PresenterError(message) from e
