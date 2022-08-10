import math
import unittest

from the_bootstrap_approach.equations import (
    sdef_t,
    propeller_advance_ratio,
    propeller_power_coefficient,
    power_adjustment_factor_x,
    atmospheric_density,
    british_standard_temperature,
)
from the_bootstrap_approach.propeller_chart import propeller_efficiency


class TestPropellerChart(unittest.TestCase):
    def test_textbook_example(self):
        self.assertTrue(
            math.isclose(
                propeller_efficiency(
                    # Dr. Lowry's example doesn't seem to account for the slowdown
                    # efficiency factor (SDEF). So, we supply a Z ratio that should
                    # yield an SDEF close to 1. It's not _exactly_ 1, but removing
                    # sdef_t from the equation only makes a difference after the 7th
                    # significant digit.
                    sdef_t(0.447487),
                    propeller_advance_ratio(253.2, 2400 / 60, 7),
                    propeller_power_coefficient(200 * 550, 0.002048, 2400 / 60, 7),
                    # power_adjustment_factor_x(200),
                    # Even though Dr. Lowry says to "Assume our blade activity factor
                    # (BAF) = 100," he comes to the conclusion that "X = 0.246." Working
                    # backwards with his formula for X, you'd actually need a BAF of
                    # 110.2310.
                    0.246,
                ),
                0.764,
                # of 3 significant digits
                abs_tol=10**-3,
            )
        )

    def test_c182rg_example(self):
        self.assertTrue(
            math.isclose(
                # These values are from the first row of Dr. Lowry's bootstp2.xls
                # spreadsheet, modeling performance of his C182RG.
                propeller_efficiency(
                    sdef_t(0.688),
                    propeller_advance_ratio(67.6762 / 0.5924838, 2300 / 60, 6.83),
                    propeller_power_coefficient(
                        0.65 * 235 * 550,
                        atmospheric_density(8000, british_standard_temperature(8000)),
                        2300 / 60,
                        6.83,
                    ),
                    power_adjustment_factor_x(195.9),
                ),
                0.616588,
                # of 6 significant digits
                abs_tol=10**-6,
            )
        )


if __name__ == "__main__":
    unittest.main()
