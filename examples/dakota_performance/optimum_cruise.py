import math
from typing import List, Optional

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
    relative_atmospheric_density,
    fts_to_kn,
    G,
    H,
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


def optimum_cruise(
    dataplate: DataPlate,
    gross_aircraft_weight: float,
    isa_diff: float = 0,
    mixture: Mixture = Mixture.BEST_POWER,
) -> PerformanceProfile:
    def func(
        pressure_altitude: float, oat_f: float
    ) -> Optional[npt.NDArray[np.float64]]:
        candidates: List[npt.NDArray[np.float64]] = []

        # The Dakota stalls at 65 KIAS at max gross weight (3000 lbf).
        stall_speed = scale_v_speed_by_weight(
            ias_to_cas(dataplate, 65), 3000, gross_aircraft_weight
        )

        best_glide_speed = calculate_best_glide(
            dataplate, gross_aircraft_weight, pressure_altitude, oat_f
        )

        # Empirically, 2200 RPM feels right for cruise. This is also the engine speed
        # that Piper references in their speed power charts.
        rpm = 2200

        full_throttle_conditions = FullThrottleConditions(
            dataplate, gross_aircraft_weight, pressure_altitude, oat_f, mixture, rpm
        )

        for power in range(
            # Between 2250 and 3000 lbf gross weights, we assume optimum cruise
            # occurs somewhere between 30–70% power.
            int(dataplate.rated_full_throttle_engine_power * 0.30),
            min(
                int(full_throttle_conditions.power),
                int(dataplate.rated_full_throttle_engine_power * 0.70),
            ),
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

            # According to Dr. Benard Carson, optimum (no-wind) cruise speed occurs at
            # approximately 3^(1/4) * VmaxLD [10, p. 4].
            approximate_carson_speed = best_glide_speed * 3 ** (1 / 4)

            table = bootstrap_cruise_performance_table(
                dataplate,
                partial_throttle_conditions,
                # Start at stall speed. At altitudes past ~12,000', there isn't
                # enough power to maintain altitude at the airframe's carson's speed.
                start=stall_speed,
                # Use a 10% buffer to account for speed variations with powerplant
                # efficiency.
                stop=approximate_carson_speed * 1.10,
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

            candidates.append(table[index_max_level_flight_speed])

        if len(candidates) > 0:
            candidates = np.array(candidates)
            fuel_flow_per_knot = candidates[:, ByKCASRowIndex.FUEL_FLOW_PER_KNOT]
            index_max_fuel_flow_per_knot = fuel_flow_per_knot.argmin()

            return candidates[index_max_fuel_flow_per_knot]

    return PerformanceProfile(
        f"Optimum (No-Wind) Cruise, {gross_aircraft_weight} lbf, ISA{isa_diff:+} ℃",
        dataplate,
        gross_aircraft_weight,
        isa_diff,
        by_altitude_profile(func, isa_diff),
    )
