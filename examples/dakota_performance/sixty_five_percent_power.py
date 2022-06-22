import numpy as np
import numpy.typing as npt

from the_bootstrap_approach.conditions import (
    FullThrottleConditions,
    PartialThrottleConditions,
)
from the_bootstrap_approach.dataplate import DataPlate
from the_bootstrap_approach.mixture import Mixture
from the_bootstrap_approach.performance import (
    ByKCASRowIndex,
    bootstrap_cruise_performance_table,
    PerformanceProfile,
    by_altitude_profile,
)


def sixty_five_percent_power(
    dataplate: DataPlate,
    gross_aircraft_weight: float,
    isa_diff: float = 0,
    mixture: Mixture = Mixture.BEST_POWER,
) -> PerformanceProfile:
    def func(pressure_altitude: float, oat_f: float) -> npt.NDArray[np.float64]:
        rpm = 2200

        full_throttle_conditions = FullThrottleConditions(
            dataplate, gross_aircraft_weight, pressure_altitude, oat_f, mixture, rpm
        )

        partial_throttle_conditions = PartialThrottleConditions(
            dataplate,
            gross_aircraft_weight,
            pressure_altitude,
            oat_f,
            mixture,
            rpm,
            dataplate.rated_full_throttle_engine_power * 0.65,
        )

        conditions = (full_throttle_conditions, partial_throttle_conditions)

        # This should tip somewhere around 8,000ft.
        winner = min(conditions, key=lambda condition: condition.power)

        table = bootstrap_cruise_performance_table(
            # 60 through 180 KCAS seemed like a reasonable
            # range. 60 is below V_{S_1} and 180 is slightly above
            # V_{NE}.
            dataplate,
            winner,
            60,
            180,
            0.1,
        )

        roc = table[:, ByKCASRowIndex.RATE_OF_CLIMB]
        index_of_highest_roc = roc.argmax()

        # VM (maximum level flight speed) occurs the second time the excess
        # power curve intersects the X-axis.
        roc_after_peak = roc[index_of_highest_roc:]
        index_max_level_flight_speed = (
            index_of_highest_roc
            + np.where(roc_after_peak > 0, roc_after_peak, np.inf).argmin()
        )

        return table[index_max_level_flight_speed]

    return PerformanceProfile(
        f"65% Power Thence Full Throttle, {gross_aircraft_weight} lbf, ISA{isa_diff:+} ℃",  # noqa
        dataplate,
        gross_aircraft_weight,
        isa_diff,
        by_altitude_profile(func, isa_diff),
    )
