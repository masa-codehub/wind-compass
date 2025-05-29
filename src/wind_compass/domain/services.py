import math
import numpy
from wind_compass.domain.models import PowerPlantModel, PolynomialCurve, Power, Torque, EffectiveWindSpeed, WindReading
from wind_compass.domain.constants import RPM_TO_RAD_PER_SEC


class PowerGenerationSimulator:
    def __init__(self, model: PowerPlantModel):
        self._model = model

    def _calculate_effective_wind_speed(self, wind_speed, wind_direction_deg, turbine_angle_deg):
        # 有効風速 = 風速 * cos(風向-タービン角)
        theta = math.radians(wind_direction_deg - turbine_angle_deg)
        cos_theta = math.cos(theta)
        # 追い風（cos_theta<0）は0とする
        if cos_theta < 0:
            return 0.0
        return wind_speed * cos_theta

    def _calculate_turbine_power(self, effective_wind_speed):
        return self._model.power_curve.calculate(effective_wind_speed)

    def _calculate_transmitted_power(self, turbine_power, efficiency):
        # 伝達効率を適用
        return turbine_power * efficiency

    def _solve_for_rpm(self, shaft_power, torque_curve: PolynomialCurve):
        # shaft_power = torque(rpm) * rpm * 2pi/60
        coeffs = list(torque_curve.coeffs)
        coeffs.append(0)  # T(rpm) * rpm → 次数+1
        coeffs = [c * RPM_TO_RAD_PER_SEC for c in coeffs]
        coeffs[-1] -= shaft_power
        roots = [r for r in numpy.roots(coeffs) if numpy.isreal(r)]
        roots = [float(r.real) for r in roots if r.real > 0]
        # 物理的に意味のある正の実数解のみを採用。複数ある場合は最小値（最も安定な回転数）を選択する仕様。
        if not roots:
            return 0.0
        rpm = min(roots)
        # 物理的に不適切なほど大きい回転数は0とみなす（例: 1e4 rpm超）
        if rpm > 1e4:
            return 0.0
        return rpm

    def _calculate_current(self, rpm):
        # 回転数から電流を計算
        return self._model.current_curve.calculate(rpm)

    def _calculate_final_power(self, current, voltage):
        # 電流と電圧から最終電力を計算
        return current * voltage

    def _is_cut_in(self, rpm, cut_in_rpm):
        # カットイン回転数判定
        return rpm >= cut_in_rpm

    def calculate_instantaneous_power(self, wind_reading: WindReading, turbine_angle_deg: float, efficiency: float, voltage: float, cut_in_rpm: float):
        # 一連の計算をオーケストレーション
        eff_ws = self._calculate_effective_wind_speed(
            wind_reading.wind_speed, wind_reading.wind_direction, turbine_angle_deg)
        if eff_ws == 0.0:
            return Power(0.0)
        turbine_power = self._calculate_turbine_power(eff_ws)
        shaft_power = self._calculate_transmitted_power(
            turbine_power, efficiency)
        rpm = self._solve_for_rpm(shaft_power, self._model.torque_curve)
        if not self._is_cut_in(rpm, cut_in_rpm):
            return Power(0.0)
        current = self._calculate_current(rpm)
        final_power = self._calculate_final_power(current, voltage)
        return Power(final_power)
