import click
from wind_compass.adapters.csv_presenter import CsvPresenter, PresenterError


def dummy_run_simulation():
    # ダミーデータ（本来はユースケースから取得）
    matrix_data = {
        'Angle 0': {'Gear 3': 100, 'Gear 5': 200},
        'Angle 22.5': {'Gear 3': 150, 'Gear 5': 250}
    }
    row_labels = ['Angle 0', 'Angle 22.5']
    col_labels = ['Gear 3', 'Gear 5']
    return matrix_data, row_labels, col_labels


@click.command()
@click.option('--output-csv', type=click.Path(dir_okay=False, writable=True, resolve_path=True), default=None, help='シミュレーション結果をCSVファイルに出力します。例: --output-csv report.csv')
def cli(output_csv):
    """
    風力発電シミュレーションCLI（ダミー実装）
    """
    # 本来はユースケース呼び出し
    matrix_data, row_labels, col_labels = dummy_run_simulation()
    # 画面表示（省略）
    if output_csv:
        try:
            presenter = CsvPresenter(filepath=output_csv)
            presenter.present(matrix_data, row_labels, col_labels)
        except ValueError as e:
            click.echo(f"Error initializing CSV presenter: {e}", err=True)
            raise SystemExit(1)
        except PresenterError as e:
            click.echo(f"Failed to generate CSV: {e}", err=True)
            raise SystemExit(1)


if __name__ == '__main__':
    cli()
