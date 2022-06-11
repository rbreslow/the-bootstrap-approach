import numpy as np
from tabulate import tabulate

from examples.dakota_performance.latex import TABLE_FORMAT
from examples.n51sw_dataplate import N51SW
from the_bootstrap_approach.conditions import Conditions, FullThrottleConditions
from the_bootstrap_approach.dataplate import DataPlate
from the_bootstrap_approach.equations import metric_standard_temperature, c_to_f
from the_bootstrap_approach.mixture import Mixture
from the_bootstrap_approach.performance import bootstrap_cruise_performance_table


def best_angle_of_climb(dataplate: DataPlate, operating_conditions: Conditions):
    """Determine Vx, best rate of climb."""
    table = bootstrap_cruise_performance_table(
        dataplate, operating_conditions, 60, 180, 0.1
    )

    aoc = table[:, 4]
    index_of_highest_aoc = aoc.argmax()
    return table[index_of_highest_aoc]


def best_rate_of_climb(dataplate: DataPlate, operating_conditions: Conditions):
    """Determine Vy, best rate of climb."""
    table = bootstrap_cruise_performance_table(
        dataplate, operating_conditions, 50, 180, 0.1
    )

    roc = table[:, 3]
    index_of_highest_roc = roc.argmax()
    return table[index_of_highest_roc]


def cruise_climb(dataplate: DataPlate, operating_conditions: Conditions):
    """Determine conditions at cruise climb, 100 KIAS."""
    table = bootstrap_cruise_performance_table(
        dataplate, operating_conditions, 100, 101, 1
    )

    return table[0]


def climb_profile_tex(profile, gross_aircraft_weight, isa_diff):
    table = tabulate(
        np.delete(profile, [2, 3, 9, 10], axis=1),
        headers=(r"$h_\rho$", "KCAS", r"$h$", r"$\gamma$", "RPM", r"\% bhp", "gph"),
        tablefmt=TABLE_FORMAT,
        floatfmt=(".0f", ".0f", ".0f", ".0f", ".0f", ".1f", ".1f"),
    )

    return f"""
\subsubsection{{{gross_aircraft_weight} lbf, ISA{isa_diff:+} \\textdegree{{C}}}}

\\textbf{{Conditions:}}
\\begin{{itemize}}
    \setlength\itemsep{{0em}}
    \item \checkitem{{Flaps}}{{Up (\\textdegree{{0}})}}
    \item \checkitem{{Power}}{{Full Throttle}}
    \item \checkitem{{Mixture}}{{Best Power}}
    \item \checkitem{{Gross Aircraft Weight}}{{{gross_aircraft_weight} lbf}}
    \item \checkitem{{Outside Air Temperature}}{{ISA{isa_diff:+} \\textdegree{{C}}}}
    \item \checkitem{{Winds}}{{Zero}}
\end{{itemize}}

{table}

\pagebreak"""


def best_rate_of_climb_tex(gross_aircraft_weight, isa_diff=0):
    profile = []
    pressure_altitude = 0

    while True:
        oat_c = metric_standard_temperature(pressure_altitude) + isa_diff

        row = best_rate_of_climb(
            N51SW,
            FullThrottleConditions(
                N51SW,
                gross_aircraft_weight,
                pressure_altitude,
                c_to_f(oat_c),
                Mixture.BEST_POWER,
                2400,
            ),
        )

        if row[4] > 0:
            profile.append(np.insert(row, 0, pressure_altitude))

            pressure_altitude += 1000
        else:
            break

    return climb_profile_tex(profile, gross_aircraft_weight, isa_diff)


def cruise_climb_tex(gross_aircraft_weight, isa_diff=0):
    profile = []

    pressure_altitude = 0  # starting pressure altitude
    while True:
        oat_c = metric_standard_temperature(pressure_altitude) + isa_diff

        row = cruise_climb(
            N51SW,
            FullThrottleConditions(
                N51SW,
                gross_aircraft_weight,
                pressure_altitude,
                c_to_f(oat_c),
                Mixture.BEST_POWER,
                2400,
            ),
        )

        if row[4] > 0:
            profile.append(np.insert(row, 0, pressure_altitude))

            pressure_altitude += 1000
        else:
            break

    return climb_profile_tex(profile, gross_aircraft_weight, isa_diff)
