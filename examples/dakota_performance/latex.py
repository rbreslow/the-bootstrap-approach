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
        climb_profile.data[
            :,
            [
                ByAltitudeRowIndex.PRESSURE_ALTITUDE,
                ByAltitudeRowIndex.KCAS,
                ByAltitudeRowIndex.RATE_OF_CLIMB,
                ByAltitudeRowIndex.FEET_PER_NAUTICAL_MILE,
                ByAltitudeRowIndex.RPM,
                ByAltitudeRowIndex.PBHP,
                ByAltitudeRowIndex.GPH,
            ],
        ],
        # When referring to these tables, rounding up to the next ISA+NN
        # will usually make up for any loss with an altimeter setting
        # less than 29.92 inHg.
        headers=(
            r"\textbf{P\textsubscript{alt}}",
            r"\textbf{KCAS}",
            r"\textbf{ft/min}",
            r"\textbf{ft/NM}",
            r"\textbf{RPM}",
            r"\textbf{\% bhp}",
            r"\textbf{gph}",
        ),
        tablefmt=TABLE_FORMAT,
        floatfmt=(".0f", ".0f", ".0f", ".0f", ".0f", ".0f", ".1f"),
    )

    return f"""
\subsection{{{climb_profile.gross_aircraft_weight} lbf, ISA{climb_profile.isa_diff:+} \\textdegree{{C}}}}

\\textbf{{Conditions:}}
\\begin{{itemize}}
    \setlength\itemsep{{0em}}
    \item \checkitem{{Flaps}}{{up (0\\textdegree{{}})}}
    \item \checkitem{{Power}}{{full throttle}}
    \item \checkitem{{Mixture}}{{full rich below 5,000 ft D\\textsubscript{{alt}} thence best power}}
    \item \checkitem{{Gross aircraft weight}}{{{climb_profile.gross_aircraft_weight} lbf}}
    \item \checkitem{{Outside air temperature}}{{ISA{climb_profile.isa_diff:+} \\textdegree{{C}}}}
    \item \checkitem{{Winds}}{{zero}}
\end{{itemize}}

{table}

\pagebreak"""  # noqa


def best_range_tex(gross_aircraft_weight: float, isa_diff: float = 0) -> str:
    cruise_profile: PerformanceProfile = best_range(
        N51SW, gross_aircraft_weight, isa_diff, Mixture.BEST_ECONOMY
    )

    table = tabulate(
        cruise_profile.data[
            :,
            [
                ByAltitudeRowIndex.PRESSURE_ALTITUDE,
                ByAltitudeRowIndex.KCAS,
                ByAltitudeRowIndex.KTAS,
                ByAltitudeRowIndex.PROPELLER_EFFICIENCY,
                ByAltitudeRowIndex.RPM,
                ByAltitudeRowIndex.PBHP,
                ByAltitudeRowIndex.GPH,
                ByAltitudeRowIndex.MPG,
            ],
        ],
        headers=(
            r"\textbf{P\textsubscript{alt}}",
            r"\textbf{KCAS}",
            r"\textbf{KTAS}",
            r"\boldmath$\eta$",
            r"\textbf{RPM}",
            r"\textbf{\% bhp}",
            r"\textbf{gph}",
            r"\textbf{mpg}",
        ),
        tablefmt=TABLE_FORMAT,
        floatfmt=(".0f", ".0f", ".0f", ".3f", ".0f", ".0f", ".1f", ".1f"),
    )

    return f"""
\subsection{{{gross_aircraft_weight} lbf, ISA{isa_diff:+} \\textdegree{{C}}}}

\\textbf{{Conditions:}}
\\begin{{itemize}}
    \setlength\itemsep{{0em}}
    \item \checkitem{{Mixture}}{{best economy}}
    \item \checkitem{{Gross aircraft weight}}{{{gross_aircraft_weight} lbf}}
    \item \checkitem{{Outside air temperature}}{{ISA{isa_diff:+} \\textdegree{{C}}}}
    \item \checkitem{{Winds}}{{zero}}
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
        cruise_profile.data[
            :,
            [
                ByAltitudeRowIndex.PRESSURE_ALTITUDE,
                ByAltitudeRowIndex.KCAS,
                ByAltitudeRowIndex.KTAS,
                ByAltitudeRowIndex.PROPELLER_EFFICIENCY,
                ByAltitudeRowIndex.RPM,
                ByAltitudeRowIndex.PBHP,
                ByAltitudeRowIndex.GPH,
                ByAltitudeRowIndex.MPG,
            ],
        ],
        headers=(
            r"\textbf{P\textsubscript{alt}}",
            r"\textbf{KCAS}",
            r"\textbf{KTAS}",
            r"\boldmath$\eta$",
            r"\textbf{RPM}",
            r"\textbf{\% bhp}",
            r"\textbf{gph}",
            r"\textbf{mpg}",
        ),
        tablefmt=TABLE_FORMAT,
        floatfmt=(".0f", ".0f", ".0f", ".3f", ".0f", ".0f", ".1f", ".1f"),
    )

    return f"""
\subsection{{{gross_aircraft_weight} lbf, ISA{isa_diff:+} \\textdegree{{C}}}}

\\textbf{{Conditions:}}
\\begin{{itemize}}
    \setlength\itemsep{{0em}}
    \item \checkitem{{Mixture}}{{best power}}
    \item \checkitem{{Gross aircraft weight}}{{{gross_aircraft_weight} lbf}}
    \item \checkitem{{Outside air temperature}}{{ISA{isa_diff:+} \\textdegree{{C}}}}
    \item \checkitem{{Winds}}{{zero}}
\end{{itemize}}
\\textbf{{Note:}} 2200 RPM is chosen as a compromise between engine vibration and
efficiency.

{table}

\pagebreak"""
