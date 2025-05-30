import click
from wind_compass.use_cases.dtos import MultipleScenariosInputDTO
from wind_compass.adapters.ui.presenters import ConsolePresenter
from wind_compass.use_cases.simulation_use_cases import RunMultipleSimulationScenariosUseCase, RunSingleSimulationScenarioUseCase
from wind_compass.adapters.data_readers import CsvWindDataReader, JsonConfigReader
from wind_compass.domain.services import PowerGenerationSimulator


def parse_float_list(ctx, param, value):
    if not value:
        return []
    result = []
    for item_str in value:
        result.extend([float(x.strip())
                      for x in item_str.split(',') if x.strip()])
    # 入力値の正規化（重複排除・昇順ソート）
    return sorted(set(result))


def get_simulate_command(
    wind_reader=None,
    config_reader=None,
    simulator_factory=None,
    single_uc=None,
    multi_uc=None,
    presenter=None
):
    wind_reader = wind_reader or CsvWindDataReader()
    config_reader = config_reader or JsonConfigReader()
    simulator_factory = simulator_factory or (
        lambda model: PowerGenerationSimulator(model))
    single_uc = single_uc or RunSingleSimulationScenarioUseCase(
        simulator_factory=simulator_factory,
        model_loader=config_reader.read,
        wind_data_reader=wind_reader
    )
    multi_uc = multi_uc or RunMultipleSimulationScenariosUseCase(single_uc)
    presenter = presenter or ConsolePresenter()

    @click.command()
    @click.option('--wind-data', type=click.Path(exists=True, dir_okay=False, readable=True), required=True, help="Path to wind data CSV file.")
    @click.option('--config-file', type=click.Path(exists=True, dir_okay=False, readable=True), required=True, help="Path to power plant model JSON config file.")
    @click.option('--angles', multiple=True, callback=parse_float_list, type=str, required=True, help="List of turbine angles (deg), e.g. --angles 0 --angles 90 or --angles 0,90")
    @click.option('--efficiency', type=float, default=None, help="Efficiency (optional)")
    @click.option('--voltage', type=float, default=None, help="Voltage (optional)")
    @click.option('--cut-in-rpm', type=float, default=None, help="Cut-in RPM (optional)")
    def simulate(wind_data, config_file, angles, efficiency, voltage, cut_in_rpm):
        """Simulate wind power generation for multiple scenarios."""
        input_dto = MultipleScenariosInputDTO(
            wind_data_path=wind_data,
            config_file_path=config_file,
            angles=angles,
            efficiency=efficiency,
            voltage=voltage,
            cut_in_rpm=cut_in_rpm,
        )
        results = multi_uc.execute(input_dto)
        click.echo(presenter.present_multiple_scenarios(
            results, angles))
    return simulate


# 後方互換のため従来のsimulateも残す
simulate = get_simulate_command()
