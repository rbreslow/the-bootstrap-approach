import numpy as np

# noinspection PyProtectedMember
from tabulate import (
    TableFormat,
    partial,
    _latex_line_begin_tabular,
    Line,
    _latex_row,
    tabulate,
)

from examples.dakota_performance import best_range, sixty_five_percent_power
from examples.n51sw_dataplate import N51SW
from the_bootstrap_approach.mixture import Mixture
from the_bootstrap_approach.performance import (
    ByAltitudeRowIndex,
    PerformanceProfile,
)

TABLE_FORMAT: TableFormat = TableFormat(
    lineabove=partial(_latex_line_begin_tabular, booktabs=True, longtable=True),
    linebelowheader=Line("\\midrule", "", "", ""),
    linebetweenrows=None,
    linebelow=Line("\\bottomrule\n\\end{longtable}", "", "", ""),
    headerrow=partial(_latex_row, escrules={}),
    datarow=_latex_row,
    padding=1,
    with_header_hide=None,
)


def climb_profile_tex(climb_profile: PerformanceProfile) -> str:
    table = tabulate(
        np.delete(
            climb_profile.data,
            [
                ByAltitudeRowIndex.KTAS,
                ByAltitudeRowIndex.PROPELLER_EFFICIENCY,
                ByAltitudeRowIndex.FUEL_FLOW_PER_KNOT,
                ByAltitudeRowIndex.MPG,
            ],
            axis=1,
        ),
        headers=(
            r"$h_\rho$",
            "KCAS",
            r"$h$ (ft/min)",
            r"$\gamma$ (ft/nm)",
            "RPM",
            r"\% bhp",
            "gph",
        ),
        tablefmt=TABLE_FORMAT,
        floatfmt=(".0f", ".0f", ".0f", ".0f", ".0f", ".1f", ".1f"),
    )

    return f"""
\subsubsection{{{climb_profile.gross_aircraft_weight} lbf, ISA{climb_profile.isa_diff:+} \\textdegree{{C}}}}

\\textbf{{Conditions:}}
\\begin{{itemize}}
    \setlength\itemsep{{0em}}
    \item \checkitem{{Flaps}}{{Up (\\textdegree{{0}})}}
    \item \checkitem{{Power}}{{Full Throttle}}
    \item \checkitem{{Mixture}}{{Full Rich $< 5000$ DA Thence Best Power}}
    \item \checkitem{{Gross Aircraft Weight}}{{{climb_profile.gross_aircraft_weight} lbf}}
    \item \checkitem{{Outside Air Temperature}}{{ISA{climb_profile.isa_diff:+} \\textdegree{{C}}}}
    \item \checkitem{{Winds}}{{Zero}}
\end{{itemize}}

{table}

\pagebreak"""  # noqa


def best_range_tex(gross_aircraft_weight: float, isa_diff: float = 0) -> str:
    cruise_profile: PerformanceProfile = best_range(
        N51SW, gross_aircraft_weight, isa_diff, Mixture.BEST_ECONOMY
    )

    table = tabulate(
        np.delete(
            cruise_profile.data,
            [
                ByAltitudeRowIndex.RATE_OF_CLIMB,
                ByAltitudeRowIndex.ANGLE_OF_CLIMB,
                ByAltitudeRowIndex.FUEL_FLOW_PER_KNOT,
            ],
            axis=1,
        ),
        headers=(
            r"$h_\rho$",
            "KCAS",
            "KTAS",
            r"$\eta$",
            "RPM",
            r"\% bhp",
            "gph",
            "mpg",
        ),
        tablefmt=TABLE_FORMAT,
        floatfmt=(".0f", ".0f", ".0f", ".3f", ".0f", ".0f", ".1f", ".1f"),
    )

    return f"""
\subsubsection{{{gross_aircraft_weight} lbf, ISA{isa_diff:+} \\textdegree{{C}}}}

\\textbf{{Conditions:}}
\\begin{{itemize}}
    \setlength\itemsep{{0em}}
    \item \checkitem{{Mixture}}{{Best Economy}}
    \item \checkitem{{Gross Aircraft Weight}}{{{gross_aircraft_weight} lbf}}
    \item \checkitem{{Outside Air Temperature}}{{ISA{isa_diff:+} \\textdegree{{C}}}}
    \item \checkitem{{Winds}}{{Zero}}
\end{{itemize}}

{table}

\pagebreak"""


def sixty_five_percent_power_thence_wot_tex(
    gross_aircraft_weight: float, isa_diff: float = 0
) -> str:
    cruise_profile = sixty_five_percent_power(
        N51SW, gross_aircraft_weight, isa_diff, Mixture.BEST_POWER
    )

    table = tabulate(
        np.delete(
            cruise_profile.data,
            [
                ByAltitudeRowIndex.RATE_OF_CLIMB,
                ByAltitudeRowIndex.ANGLE_OF_CLIMB,
                ByAltitudeRowIndex.FUEL_FLOW_PER_KNOT,
            ],
            axis=1,
        ),
        headers=(
            r"$h_\rho$",
            "KCAS",
            "KTAS",
            r"$\eta$",
            "RPM",
            r"\% bhp",
            "gph",
            "mpg",
        ),
        tablefmt=TABLE_FORMAT,
        floatfmt=(".0f", ".0f", ".0f", ".3f", ".0f", ".0f", ".1f", ".1f"),
    )

    return f"""
\subsubsection{{{gross_aircraft_weight} lbf, ISA{isa_diff:+} \\textdegree{{C}}}}

\\textbf{{Conditions:}}
\\begin{{itemize}}
    \setlength\itemsep{{0em}}
    \item \checkitem{{Mixture}}{{Best Power}}
    \item \checkitem{{Gross Aircraft Weight}}{{{gross_aircraft_weight} lbf}}
    \item \checkitem{{Outside Air Temperature}}{{ISA{isa_diff:+} \\textdegree{{C}}}}
    \item \checkitem{{Winds}}{{Zero}}
\end{{itemize}}
\\textbf{{Note:}} 2200 RPM is chosen as a compromise between engine vibration and
efficiency.

{table}

\pagebreak"""
