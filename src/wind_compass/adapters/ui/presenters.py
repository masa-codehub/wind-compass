from typing import List
from tabulate import tabulate
from wind_compass.use_cases.dtos import ScenarioResult


class ConsolePresenter:
    def present_multiple_scenarios(self, results: List[ScenarioResult], angles: List[float]) -> str:
        if not results:
            return "No simulation results to present."
        # angle -> annual_power_kwh or error
        results_map = {
            r.angle: r.annual_power_kwh if r.error_message is None else f"Error: {r.error_message[:20]}" for r in results}
        table_data = []
        header = ["Angle (deg)", "Annual Power (kWh)"]
        table_data.append(header)
        for angle in sorted(set(angles)):
            val = results_map.get(angle, "N/A")
            if isinstance(val, float):
                row = [f"{angle:.2f}", f"{val:.2f} kWh"]
            else:
                row = [f"{angle:.2f}", str(val)]
            table_data.append(row)
        return tabulate(table_data, headers="firstrow", tablefmt="grid")
