import numpy as np
import numpy.typing as npt
from the_bootstrap_approach.conditions import FullThrottleConditions
from the_bootstrap_approach.dataplate import DataPlate
from the_bootstrap_approach.equations import density_altitude
from the_bootstrap_approach.mixture import Mixture
from the_bootstrap_approach.performance import (
    bootstrap_cruise_performance_table,
    ByKCASRowIndex,
    by_altitude_profile,
    PerformanceProfile,
)


def best_rate_of_climb(
    dataplate: DataPlate, gross_aircraft_weight: float, isa_diff: float = 0
) -> PerformanceProfile:
    def func(pressure_altitude: float, oat_f: float) -> npt.NDArray[np.float64]:
        mixture = Mixture.BEST_POWER

        # Below 5,000' DA (~85% Power), we need to use a full rich mixture.
        if density_altitude(pressure_altitude, oat_f) < 5000:
            mixture = Mixture.FULL_RICH

        operating_conditions = FullThrottleConditions(
            dataplate,
            gross_aircraft_weight,
            pressure_altitude,
            oat_f,
            mixture,
            dataplate.rated_full_throttle_engine_rpm,
        )

        table = bootstrap_cruise_performance_table(
            # See how the aircraft behaves under these conditions from 50
            # through 180 KCAS.
            dataplate,
            operating_conditions,
            50,
            180,
            0.1,
        )

        roc = table[:, ByKCASRowIndex.RATE_OF_CLIMB]
        index_of_highest_roc = roc.argmax()
        return table[index_of_highest_roc]

    return PerformanceProfile(
        f"Best Rate of Climb {gross_aircraft_weight} lbf, ISA{isa_diff:+} ℃",
        dataplate,
        gross_aircraft_weight,
        isa_diff,
        by_altitude_profile(func, isa_diff),
    )
