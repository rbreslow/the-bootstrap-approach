import unittest

import math

from the_bootstrap_approach.equations import (
    altitude_power_dropoff_factor,
    atmospheric_density,
    power_adjustment_factor_x,
    propeller_advance_ratio,
    propeller_power_coefficient,
    relative_atmospheric_density_alt,
    sdef_t,
    scale_v_speed_by_weight,
)


class TestEquations(unittest.TestCase):
    def test_atmospheric_density(self):
        # TBA Field Guide Pg. 1
        self.assertTrue(
            math.isclose(
                atmospheric_density(0.88808),
                0.002111,
                # of 4 significant digits
                abs_tol=10**-6,
            )
        )

    def test_altitude_power_dropoff_factor(self):
        # Compared against the Lycoming Operator's Manual for the O-540-J35AD.
        self.assertTrue(
            math.isclose(
                altitude_power_dropoff_factor(relative_atmospheric_density_alt(59, 0))
                * 235,
                235,
                # of 0 significant digits
                abs_tol=10**-0,
            )
        )
        self.assertTrue(
            math.isclose(
                altitude_power_dropoff_factor(
                    relative_atmospheric_density_alt(-4, 17500)
                )
                * 235,
                122,
                # of 0 significant digits
                abs_tol=10**-0,
            )
        )

    def test_sdef_t(self):
        # From Dr. Lowry's bootstp2.xls example.
        self.assertTrue(
            math.isclose(
                sdef_t(0.688),
                0.910,
                # of 3 significant digits
                abs_tol=10**-3,
            )
        )

    def test_propeller_advance_ratio(self):
        # Pg. 178, Example 6.4
        self.assertTrue(
            math.isclose(
                propeller_advance_ratio(253.2, 2400 / 60, 7),
                0.9043,
                # of 4 significant digits
                abs_tol=10**-4,
            )
        )

    def test_propeller_power_coefficient(self):
        # Pg. 178, Example 6.4
        self.assertTrue(
            math.isclose(
                propeller_power_coefficient(200 * 550, 0.002048, 2400 / 60, 7),
                0.04993,
                # of 5 significant digits
                abs_tol=10**-5,
            )
        )

    def test_power_adjustment_factor(self):
        # From Dr. Lowry's bootstp2.xls example.
        self.assertTrue(
            math.isclose(
                power_adjustment_factor_x(195.9),
                0.2088,
                # of 4 significant digits
                abs_tol=10**-4,
            )
        )

    def test_scale_v_speed_by_weight(self):
        # > According to Table 7.4, when our sample Cessna 172 is at 8000 ft
        # > weighing 1800 lb, Vx = 54.7 KCAS. What would Vx be if, instead, it
        # > weighed 100 lb more, 1900 lb?
        #
        # > So, the new Vx, for the higher weight, is about 54.7 + 1.5 = 56.2
        # > KCAS.
        # [1, p. 210]
        print(scale_v_speed_by_weight(54.7, 1800, 1900))
        self.assertTrue(
            math.isclose(
                scale_v_speed_by_weight(54.7, 1800, 1900),
                56.2,
                # of 1 significant digits
                abs_tol=10**-1,
            )
        )


if __name__ == "__main__":
    unittest.main()
