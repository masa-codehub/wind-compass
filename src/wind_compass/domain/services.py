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
        # torque_curve: krpm基準
        # shaft_power = T_gen(rpm_gen/1000) * rpm_gen * 2pi/60
        # T_gen(x_krpm) = c3 x_krpm^3 + ... + c0
        # x_krpm = rpm_gen / 1000
        # T_gen(rpm_gen) = c3 (rpm_gen/1000)^3 + ...
        # 多項式係数をrpm基準にスケーリング
        orig_coeffs = list(torque_curve.coeffs)
        degree = len(orig_coeffs) - 1
        scaled_coeffs = []
        for i, c in enumerate(orig_coeffs):
            scaled_coeffs.append(c / (1000 ** (degree - i)))
        # T(rpm) * rpm
        coeffs = list(scaled_coeffs)
        coeffs.append(0)  # T(rpm) * rpm → 次数+1
        coeffs = [c * RPM_TO_RAD_PER_SEC for c in coeffs]
        coeffs[-1] -= shaft_power
        roots = [r for r in numpy.roots(coeffs) if numpy.isreal(r)]
        roots = [float(r.real) for r in roots if r.real > 0]
        if not roots:
            return 0.0
        rpm = min(roots)
        if rpm > 1e4:
            return 0.0
        return rpm

    def _calculate_current(self, rpm):
        # 回転数から電流を計算
        # current_curveもkrpm基準
        return self._model.current_curve.calculate(rpm / 1000)

    def _calculate_final_power(self, current, voltage):
        # 電流と電圧から最終電力を計算
        return current * voltage

    def _is_cut_in(self, rpm, cut_in_rpm):
        # カットイン回転数判定
        return rpm >= cut_in_rpm

    def calculate_instantaneous_power(self, wind_reading: WindReading, turbine_angle_deg: float, efficiency: float, voltage: float, cut_in_rpm: float):
        eff_ws = self._calculate_effective_wind_speed(
            wind_reading.wind_speed, wind_reading.wind_direction, turbine_angle_deg)
        if eff_ws == 0.0:
            return Power(0.0)
        turbine_power = self._calculate_turbine_power(eff_ws)
        shaft_power = self._calculate_transmitted_power(
            turbine_power, efficiency)
        rpm_gen = self._solve_for_rpm(shaft_power, self._model.torque_curve)
        if not self._is_cut_in(rpm_gen, cut_in_rpm):
            return Power(0.0)
        current = self._calculate_current(rpm_gen)
        final_power = self._calculate_final_power(current, voltage)
        return Power(final_power)
