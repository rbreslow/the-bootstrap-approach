import numpy as np
import numpy.typing as npt

from examples.n51sw_dataplate import N51SW
from the_bootstrap_approach.airspeed_calibration import ias_to_cas
from the_bootstrap_approach.conditions import FullThrottleConditions
from the_bootstrap_approach.dataplate import DataPlate
from the_bootstrap_approach.equations import density_altitude
from the_bootstrap_approach.mixture import Mixture
from the_bootstrap_approach.performance import (
    bootstrap_cruise_performance_table,
    by_altitude_profile,
    PerformanceProfile,
    ByKCASRowIndex,
)


def cruise_climb(
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

        cruise_climb_cas = ias_to_cas(N51SW, 100)

        row = bootstrap_cruise_performance_table(
            dataplate, operating_conditions, cruise_climb_cas, cruise_climb_cas + 1, 1
        )[0]

        target_airspeed = cruise_climb_cas
        target_fpm = 200

        while row[ByKCASRowIndex.RATE_OF_CLIMB] < target_fpm:
            row = bootstrap_cruise_performance_table(
                dataplate, operating_conditions, target_airspeed - 1, target_airspeed, 1
            )[0]
            target_airspeed -= 1

            # Once it's impossible to climb at this target rate, set a lower
            # target and reset the search.
            if row[ByKCASRowIndex.KCAS] == 50:
                target_airspeed = cruise_climb_cas
                target_fpm -= 10

            # We've hit our ceiling.
            if target_fpm <= 0:
                break

        return row

    return PerformanceProfile(
        f"100 KIAS Cruise Climb {gross_aircraft_weight} lbf, ISA{isa_diff:+} ℃",
        dataplate,
        gross_aircraft_weight,
        isa_diff,
        by_altitude_profile(func, isa_diff),
    )
