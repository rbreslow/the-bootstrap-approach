import math
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Callable

import numpy as np
import numpy.typing as npt

from the_bootstrap_approach.conditions import (
    Conditions,
)
from the_bootstrap_approach.dataplate import DataPlate
from the_bootstrap_approach.equations import (
    tas,
    kn_to_fts,
    sdef_t,
    propeller_advance_ratio,
    propeller_power_coefficient,
    power_adjustment_factor_x,
    power_required,
    power_available,
    metric_standard_temperature,
    c_to_f,
    fuel_lbf_to_gal,
    ft_lbfs_to_hp,
)
from the_bootstrap_approach.propeller_chart import propeller_efficiency


class ByKCASRowIndex(IntEnum):
    KCAS = 0
    KTAS = 1
    PROPELLER_EFFICIENCY = 2
    THRUST = 3
    DRAG = 4
    RATE_OF_CLIMB = 5
    ANGLE_OF_CLIMB = 6
    FEET_PER_NAUTICAL_MILE = 7
    POWER_REQUIRED = 8
    POWER_AVAILABLE = 9
    EXCESS_POWER = 10
    RPM = 11
    PBHP = 12
    GPH = 13
    FUEL_FLOW_PER_KNOT = 14
    MPG = 15


class ByAltitudeRowIndex(IntEnum):
    PRESSURE_ALTITUDE = 0
    KCAS = 1
    KTAS = 2
    PROPELLER_EFFICIENCY = 3
    THRUST = 4
    DRAG = 5
    RATE_OF_CLIMB = 6
    ANGLE_OF_CLIMB = 7
    FEET_PER_NAUTICAL_MILE = 8
    POWER_REQUIRED = 9
    POWER_AVAILABLE = 10
    EXCESS_POWER = 11
    RPM = 12
    PBHP = 13
    GPH = 14
    FUEL_FLOW_PER_KNOT = 15
    MPG = 16


def bootstrap_cruise_performance_table(
    dataplate: DataPlate,
    operating_conditions: Conditions,
    start,
    stop,
    step,
    headwind=0,
) -> np.ndarray:
    kcas = np.arange(start, stop, step)
    ktas = tas(kcas, operating_conditions.relative_atmospheric_density) + headwind
    vt = kn_to_fts(ktas)

    eta = propeller_efficiency(
        sdef_t(dataplate.z_ratio),
        propeller_advance_ratio(
            vt,
            operating_conditions.propeller_rps,
            dataplate.propeller_diameter,
        ),
        propeller_power_coefficient(
            operating_conditions.power,
            operating_conditions.atmospheric_density,
            operating_conditions.propeller_rps,
            dataplate.propeller_diameter,
        ),
        power_adjustment_factor_x(dataplate.total_activity_factor),
    )

    pre = power_required(operating_conditions.g, operating_conditions.h, vt)
    pav = power_available(eta, operating_conditions.power)
    pxs = pav - pre

    thrust = pav / vt
    drag = pre / vt
    excess_thrust = thrust - drag

    roc = 60 * excess_thrust * vt / operating_conditions.gross_aircraft_weight
    aoc = (180 / math.pi) * np.arcsin(
        excess_thrust / operating_conditions.gross_aircraft_weight
    )
    ftnm = roc / (ktas / 60)

    # Divide by 550 ft-lbf/s to get brake horsepower (BHP).
    power = np.full(kcas.size, operating_conditions.power)

    rpm = np.full(kcas.size, operating_conditions.engine_rpm)
    pbhp = (power / dataplate.rated_full_throttle_engine_power) * 100

    # The volume of aviation fuel varies with air density [8, p. 9-14].
    gph = fuel_lbf_to_gal(
        # bsfc is measured in lbs./BHP./hr. So, bsfc * BHP yields fuel lbs./hr.
        operating_conditions.bsfc * ft_lbfs_to_hp(power),
        operating_conditions.oat_f,
    )

    # https://aviation.stackexchange.com/questions/63976/what-is-carson-cruise-and-can-i-determine-it-myself
    fuel_flow_per_knot = thrust / vt
    mpg = ktas / gph

    return np.column_stack(
        (
            kcas,
            ktas,
            eta,
            thrust,
            drag,
            roc,
            aoc,
            ftnm,
            pre,
            pav,
            pxs,
            rpm,
            pbhp,
            gph,
            fuel_flow_per_knot,
            mpg,
        )
    )


@dataclass(frozen=True)
class PerformanceProfile:
    name: str
    dataplate: DataPlate
    gross_aircraft_weight: float
    isa_diff: float
    data: npt.NDArray[npt.NDArray[np.float64]]


def by_altitude_profile(
    func: Callable[[float, float], Optional[npt.NDArray[np.float64]]],
    isa_diff: float = 0,
) -> npt.NDArray[npt.NDArray[np.float64]]:
    profile = []
    pressure_altitude = 0

    while True:
        oat_c = metric_standard_temperature(pressure_altitude) + isa_diff

        row = func(pressure_altitude, c_to_f(oat_c))

        if row is not None and row[ByKCASRowIndex.RATE_OF_CLIMB] > 0:
            profile.append(np.insert(row, 0, pressure_altitude))
            pressure_altitude += 1000
        else:
            # The aircraft isn't sustaining level flight if the rate of climb
            # is negative, so we know we've reached absolute ceiling.
            break

    return np.array(profile)
