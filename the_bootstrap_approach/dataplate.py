from the_bootstrap_approach.equations import engine_torque
from the_bootstrap_approach.mixture import Mixture


class DataPlate:
    def __init__(
        self,
        configuration,
        reference_wing_area,
        wing_span,
        parasite_drag_coefficient,
        airplane_efficiency_factor,
        rated_full_throttle_engine_horsepower,
        rated_full_throttle_engine_rpm,
        engine_power_altitude_dropoff_parameter,
        bsfc,
        propeller_diameter,
        blade_activity_factor,
        z_ratio,
    ):
        # Airplane configuration. e.g., flaps/gear position.
        self.configuration = configuration
        # S, reference wing area (ft^2).
        self.reference_wing_area = reference_wing_area
        # B, wing span (ft).
        self.wing_span = wing_span
        # A, wing aspect ratio (span^2/S).
        self.wing_aspect_ratio = wing_span**2 / reference_wing_area
        # C_{D0}, parasite drag coefficient (depends on flaps/gear configuration).
        self.parasite_drag_coefficient = parasite_drag_coefficient
        # e, airplane efficiency factor (possibly depends on flaps configuration).
        self.airplane_efficiency_factor = airplane_efficiency_factor
        # P_0, rated MSL shaft power at rated RPM.
        self.rated_full_throttle_engine_horsepower = 235
        # P_0, rated MSL power (ft-lbf/sec)
        self.rated_full_throttle_engine_power = (
            rated_full_throttle_engine_horsepower * 550
        )
        # N_0, rated MSL full-throttle RPM.
        self.rated_full_throttle_engine_rpm = rated_full_throttle_engine_rpm
        # n_0, rated MSL full-throttle RPS.
        self.rated_full_throttle_propeller_rps = rated_full_throttle_engine_rpm / 60
        # M_0, rated full-throttle engine torque (ft-lbf).
        self.rated_full_throttle_engine_torque = engine_torque(
            self.rated_full_throttle_engine_power,
            self.rated_full_throttle_propeller_rps,
        )
        # C, engine power altitude dropoff parameter, the porportion of indicated
        # power that goes to engine friction losses (close to 0.12).
        self.engine_power_altitude_dropoff_parameter = (
            engine_power_altitude_dropoff_parameter
        )
        # c, brake specific full consumption rate (lbm/HP/HR).
        self._bsfc = bsfc
        # d, propeller diameter (ft).
        self.propeller_diameter = propeller_diameter
        # BAF, blade activity factor.
        self.blade_activity_factor = blade_activity_factor
        # TAF, total activity factor.
        self.total_activity_factor = blade_activity_factor * 2
        # Z, ratio of fuselage diameter (taken one propeller diameter behind the
        # propeller) to propeller diameter.
        self.z_ratio = z_ratio

    def bsfc(self, mixture: Mixture):
        if mixture == Mixture.BEST_POWER:
            return self._bsfc[0]
        elif mixture == Mixture.BEST_ECONOMY:
            return self._bsfc[1]
        elif mixture == Mixture.FULL_RICH:
            return self._bsfc[2]
