import numpy as np

from examples.n51sw_dataplate import N51SW
from the_bootstrap_approach.conditions import (
    FullThrottleConditions,
    PartialThrottleConditions,
)
from the_bootstrap_approach.dataplate import DataPlate
from the_bootstrap_approach.performance import bootstrap_cruise_performance_table


def best_range_and_optimum_cruise(
    dataplate: DataPlate, gross_aircraft_weight, pressure_altitude, oat_f, mixture
):
    """Determine Vbr and Vcr (?), best range and optimum cruise conditions."""
    best_range_candidates = []
    optimum_cruise_candidates = []

    # Get full throttle conditions for every 50 RPM. 1800-2400 is the range
    # of acceptable RPM at any MAP according to the O-540-J35AD performance
    # curves.
    for rpm in range(1750, 2450, 50):
        full_throttle_conditions = FullThrottleConditions(
            dataplate, gross_aircraft_weight, pressure_altitude, oat_f, mixture, rpm
        )

        # Now, try every horsepower possible for that engine at that RPM. Start
        # at 50 HP, since the plane can't even sustain flight below that at MSL,
        # and the propeller simulation starts to get wonky.
        for power in range(50 * 550, int(full_throttle_conditions.power), 550):
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
                # 60 KCAS through 180 KCAS seemed like a reasonable
                # range. 60 is below V_{S_1} and 180 is slightly above
                # V_{NE}.
                dataplate,
                partial_throttle_conditions,
                60,
                180,
                0.1,
            )

            # V_y, best rate of climb.
            roc = table[:, 3]
            index_of_highest_roc = roc.argmax()

            # V_m, minimum level flight speed (in practice, Vm seldom occurs, because
            # the power-on stall speed is usually much higher).
            roc_before_peak = roc[:index_of_highest_roc]
            if roc_before_peak.size > 0:
                index_min_level_flight_speed = np.where(
                    roc_before_peak > 0, roc_before_peak, np.inf
                ).argmin()
            else:
                index_min_level_flight_speed = 0

            # V_M, maximum level flight speed.
            roc_after_peak = roc[index_of_highest_roc:]
            index_max_level_flight_speed = np.where(
                roc_after_peak > 0, roc_after_peak, np.inf
            ).argmin()

            # mpg, nautical miles per gallon.
            mpg = table[:, 9][: index_of_highest_roc + index_max_level_flight_speed]
            if mpg.size > 0:
                index_max_mpg = mpg.argmax()
                best_range_candidates.append(table[index_max_mpg])

            # Fuel Flow / knot (where this parameter is at a minimum we've found
            # Carson's speed).
            fuel_flow_per_knot = table[:, 8][
                index_min_level_flight_speed : index_of_highest_roc
                + index_max_level_flight_speed
            ]

            # We can't consider any negative ROCs.
            for idx, _ in enumerate(fuel_flow_per_knot):
                if roc[idx] < 0:
                    fuel_flow_per_knot[idx] = np.inf

            if fuel_flow_per_knot.size > 0:
                index_min_fuel_flow_per_knot = fuel_flow_per_knot.argmin()
                optimum_cruise_candidates.append(table[index_min_fuel_flow_per_knot])

    # mpg, nautical miles per gallon.
    best_range_candidates = np.array(best_range_candidates)
    mpg = best_range_candidates[:, 9]
    index_max_mpg = mpg.argmax()

    # Fuel Flow / knot (where this parameter is at a minimum we've found
    # Carson's speed).
    optimum_cruise_candidates = np.array(optimum_cruise_candidates)
    fuel_flow_per_knot = optimum_cruise_candidates[:, 8]
    index_min_fuel_flow_per_knot = fuel_flow_per_knot.argmin()

    return (
        best_range_candidates[index_max_mpg],
        optimum_cruise_candidates[index_min_fuel_flow_per_knot],
    )
