from typing import List, Optional

import math
import numpy as np
import numpy.typing as npt

from the_bootstrap_approach.airspeed_calibration import ias_to_cas
from the_bootstrap_approach.conditions import (
    FullThrottleConditions,
    PartialThrottleConditions,
)
from the_bootstrap_approach.dataplate import DataPlate
from the_bootstrap_approach.equations import (
    atmospheric_density,
    scale_v_speed_by_weight,
    G,
    H,
    relative_atmospheric_density,
    fts_to_kn,
)
from the_bootstrap_approach.mixture import Mixture
from the_bootstrap_approach.performance import (
    ByKCASRowIndex,
    bootstrap_cruise_performance_table,
    PerformanceProfile,
    by_altitude_profile,
)


def calculate_best_glide(
    dataplate: DataPlate,
    gross_aircraft_weight: float,
    pressure_altitude: float,
    oat_f: float,
) -> float:
    sigma = relative_atmospheric_density(pressure_altitude, oat_f)
    rho = atmospheric_density(pressure_altitude, oat_f)

    g = G(
        rho,
        dataplate.reference_wing_area,
        dataplate.parasite_drag_coefficient,
    )

    h = H(
        gross_aircraft_weight,
        rho,
        dataplate.reference_wing_area,
        dataplate.airplane_efficiency_factor,
        dataplate.wing_aspect_ratio,
    )

    u = h / g

    return fts_to_kn(math.sqrt(sigma) * u ** (1 / 4))


def best_range(
    dataplate: DataPlate,
    gross_aircraft_weight: float,
    isa_diff: float = 0,
    mixture: Mixture = Mixture.BEST_POWER,
) -> PerformanceProfile:
    def func(
        pressure_altitude: float, oat_f: float
    ) -> Optional[npt.NDArray[np.float64]]:
        best_range_candidates: List[npt.NDArray[np.float64]] = []

        # The Dakota stalls at 65 KIAS at max gross weight (3000 lbf).
        stall_speed = scale_v_speed_by_weight(
            ias_to_cas(dataplate, 65), 3000, gross_aircraft_weight
        )

        best_glide_speed = calculate_best_glide(
            dataplate, gross_aircraft_weight, pressure_altitude, oat_f
        )

        # Lycoming's O-540-J performance data shows that between 2400 and 1800
        # RPM, you can use any MAP setting below 29 inHg (e.g., full throttle).
        for rpm in range(1800, 2500, 100):
            full_throttle_conditions = FullThrottleConditions(
                dataplate, gross_aircraft_weight, pressure_altitude, oat_f, mixture, rpm
            )

            for power in range(
                # TODO: The model gets wonky below ~5% brake horsepower.
                int(dataplate.rated_full_throttle_engine_power * 0.05),
                int(full_throttle_conditions.power),
                550,
            ):
                partial_throttle_conditions = PartialThrottleConditions(
                    dataplate,
                    gross_aircraft_weight,
                    pressure_altitude,
                    oat_f,
                    mixture,
                    rpm,
                    power,
                )

                table = bootstrap_cruise_performance_table(
                    dataplate,
                    partial_throttle_conditions,
                    # In a simplified theory in which propeller efficiency and
                    # specific fuel consumption are constant, best range speed
                    # is the speed for best glide. Our calculations improve
                    # realism in that propeller efficiency varies with air
                    # speed, and closely following the engine manual for the
                    # Piper Dakota's Lycoming O-540-J3A5D engine, c is taken
                    # to be only piecewise constant.
                    start=max(stall_speed, best_glide_speed - 20),
                    stop=best_glide_speed + 20,
                    step=0.1,
                )

                roc = table[:, ByKCASRowIndex.RATE_OF_CLIMB]
                # If all the ROCs are less than 0 ft/min, then the airplane
                # can't sustain level flight in these conditions.
                if (roc < 0).all():
                    continue
                index_of_highest_roc = roc.argmax()

                # VM (maximum level flight speed) occurs the second time the
                # excess power curve intersects the X-axis.
                roc_after_peak = roc[index_of_highest_roc:]
                index_max_level_flight_speed = (
                    index_of_highest_roc
                    + np.where(roc_after_peak > 0, roc_after_peak, np.inf).argmin()
                )

                best_range_candidates.append(table[index_max_level_flight_speed])

        if len(best_range_candidates) > 0:
            best_range_candidates = np.array(best_range_candidates)
            mpg = best_range_candidates[:, ByKCASRowIndex.MPG]
            index_max_mpg = mpg.argmax()

            return best_range_candidates[index_max_mpg]

    return PerformanceProfile(
        f"Best Range, {gross_aircraft_weight} lbf, ISA{isa_diff:+} ℃",
        dataplate,
        gross_aircraft_weight,
        isa_diff,
        by_altitude_profile(func, isa_diff),
    )
