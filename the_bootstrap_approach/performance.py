import math

import numpy as np

from the_bootstrap_approach.conditions import (
    Conditions,
    FullThrottleConditions,
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
)
from the_bootstrap_approach.propeller_chart import propeller_efficiency


INDEX_KCAS = 0
INDEX_KTAS = 1
INDEX_ETA = 2
INDEX_ROC = 3
INDEX_FTNM = 4
INDEX_RPM = 5
INDEX_PHBP = 6
INDEX_GPH = 7
INDEX_FUEL_FLOW_PER_KNOT = 8
INDEX_MPG = 9


def bootstrap_cruise_performance_table(
    dataplate: DataPlate,
    operating_conditions: Conditions,
    min,
    max,
    step,
    expanded=False,
):
    kcas = np.arange(min, max, step)
    ktas = tas(kcas, operating_conditions.relative_atmospheric_density)
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

    rpm = np.full(len(kcas), operating_conditions.engine_rpm)
    if type(operating_conditions) == FullThrottleConditions:
        # %bhp and GPH at full throttle for these operating conditions.
        # TODO: What happens if someone brings RPM back? Does this still work?
        # Or, since we're already multiplying by ETA, are we all good?
        pbhp = ((pav / eta) / dataplate.rated_full_throttle_engine_power) * 100
        gph = (operating_conditions.bsfc * (pav / eta) / 550) / 6
    else:
        # %bhp and GPH required to maintain level flight at this TAS.
        pbhp = ((pre / eta) / dataplate.rated_full_throttle_engine_power) * 100
        gph = (operating_conditions.bsfc * (pre / eta) / 550) / 6
    fuel_flow_per_knot = thrust / vt
    mpg = ktas / gph

    if expanded:
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
    else:
        return np.column_stack(
            (kcas, ktas, eta, roc, ftnm, rpm, pbhp, gph, fuel_flow_per_knot, mpg)
        )
