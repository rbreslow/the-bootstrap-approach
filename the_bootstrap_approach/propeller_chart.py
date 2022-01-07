import math
import numpy as np

# Dr. Lowry states:
# > Data and measurements for a general aviation constant-speed propeller let us
# > construct such a chart (see Fig. 6.19).
# This object is a representation of the coefficients that form Dr. Lowry's
# chart.
propeller_chart = {
    0.15: [
        -0.0272805419249278,
        1.15781894222425,
        -0.548923123012512,
        0.0385516502694899,
        0.064580555280077,
        -0.0263012433108758,
        0.00301741988065448,
    ],
    0.25: [
        -0.0385029968953664,
        1.04613581578757,
        -0.485313329667262,
        0.130100232509281,
        -0.0273266101237454,
        0.00313901396067647,
        -0.000131566344754572,
    ],
    0.40: [
        -0.026741905,
        0.7175824135,
        -0.08467335,
        -0.07445168,
        0.026437051,
        -0.003537565,
        0.000177733,
    ],
    0.60: [
        0.0381002521517944,
        0.199522455590403,
        0.458898025445346,
        -0.3189927366795,
        0.0813578214054723,
        -0.00908380171181081,
        0.000350613125807782,
    ],
    0.80: [
        0.251897476,
        -0.56166584,
        1.13905513,
        -0.60219333,
        0.144341736,
        -0.01619473,
        0.000664038,
    ],
    1.00: [
        0.140144145675375,
        0.0716361297937569,
        -0.0573564176265628,
        0.276378945894403,
        -0.159843307010587,
        0.0342398462584903,
        -0.00257300278564554,
    ],
    1.20: [
        -0.705604050000001,
        2.868232531,
        -3.651371295,
        2.487262933,
        -0.863421200000001,
        0.1464783315,
        -0.00968685500000001,
    ],
    1.40: [
        -2.34053218393923,
        7.56393789714959,
        -9.02096499247491,
        5.55004513329438,
        -1.79377691748934,
        0.291020480453595,
        -0.0187431693125258,
    ],
}


def propeller_efficiency(
    sdef,
    propeller_advance_ratio,
    propeller_power_coefficient,
    power_adjustment_factor_x,
):
    """Approximates η, constant-speed propulsive efficiency:

    :math:`\eta = {SDEF(Z)} \\times \eta(J/C_p{}^\\frac{1}{3}{}^2, C_{PX})`

    Args:
        z_ratio: :math:`Z`, ratio of fuselage diameter to propeller diameter.
        propeller_advance_ratio: :math:`J`, propeller advance ratio.
        propeller_power_coefficient: :math:`C_P`, propeller power coefficient.
        power_adjustment_factor_x: :math:`X`, power adjustment factor.

    Returns:
        :math:`\eta`, propeller efficiency.
    """
    curves = list(propeller_chart.keys())

    # $C_{PX} = C_P / X$
    adjusted_propeller_power_coefficient = (
        propeller_power_coefficient / power_adjustment_factor_x
    )

    i = np.searchsorted(curves, adjusted_propeller_power_coefficient, side="right") - 1

    left_interpolation_factor = (
        curves[i + 1] - adjusted_propeller_power_coefficient
    ) / (curves[i + 1] - curves[i])
    right_interpolation_factor = (adjusted_propeller_power_coefficient - curves[i]) / (
        curves[i + 1] - curves[i]
    )

    def interpolated_coefficient(left_curve_idx, power):
        return (
            left_interpolation_factor * propeller_chart[curves[left_curve_idx]][power]
            + right_interpolation_factor
            * propeller_chart[curves[left_curve_idx + 1]][power]
        )

    coefficients = {
        0: interpolated_coefficient(i, 0),
        1: interpolated_coefficient(i, 1),
        2: interpolated_coefficient(i, 2),
        3: interpolated_coefficient(i, 3),
        4: interpolated_coefficient(i, 4),
        5: interpolated_coefficient(i, 5),
        6: interpolated_coefficient(i, 6),
    }

    # x, in this case, is $J/C_P{}^\frac{1}{3}{}^2$.
    x = propeller_advance_ratio / propeller_power_coefficient ** (1 / 3)

    # $\eta = \mathit{SDEF(Z)} \times \eta(J/C_p{}^\frac{1}{3}{}^2, C_{PX})$
    return sdef * (
        coefficients[0]
        + (coefficients[1] * x)
        + (coefficients[2] * x ** 2)
        + (coefficients[3] * x ** 3)
        + (coefficients[4] * x ** 4)
        + (coefficients[5] * x ** 5)
        + (coefficients[6] * x ** 6)
    )
