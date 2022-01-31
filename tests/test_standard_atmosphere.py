import unittest

import math

from the_bootstrap_approach.equations import (
    british_standard_temperature,
    c_to_f,
    density_altitude,
    f_to_c,
    metric_standard_temperature,
)


class TestStandardAtmosphere(unittest.TestCase):
    def setUp(self):
        # This table is from Chapter 4 of the Pilot's Handbook of Aeronautical
        # Knowledge [8, p. 4-3].
        self.phak_standard_atmosphere = (
            (15.0, 59.0),
            (13.0, 55.4),
            (11.0, 51.9),
            (9.1, 48.3),
            (7.1, 44.7),
            (5.1, 41.2),
            (3.1, 37.6),
            (1.1, 34.0),
            (-0.9, 30.5),
            (-2.8, 26.9),
            (-4.8, 23.3),
            (-6.8, 19.8),
            (-8.8, 16.2),
            (-10.8, 12.6),
            (-12.7, 9.1),
            (-14.7, 5.5),
            (-16.7, 1.9),
            (-18.7, -1.6),
            (-20.7, -5.2),
            (-22.6, -8.8),
            (-24.6, -12.3),
        )

        pass

    def test_phak_standard_atmosphere(self):
        for i in range(len(self.phak_standard_atmosphere)):
            altitude = i * 1000
            oat_c, oat_f = self.phak_standard_atmosphere[i]

            self.assertTrue(
                math.isclose(
                    metric_standard_temperature(altitude),
                    oat_c,
                    # of 1 significant digits
                    abs_tol=10**-1,
                )
            )

            self.assertTrue(
                math.isclose(
                    british_standard_temperature(altitude),
                    oat_f,
                    # of 1 significant digits
                    abs_tol=10**-1,
                )
            )

    def test_temperature_conversions(self):
        for i in range(len(self.phak_standard_atmosphere)):
            altitude = i * 1000
            oat_c, oat_f = self.phak_standard_atmosphere[i]

            self.assertTrue(
                math.isclose(
                    f_to_c(british_standard_temperature(altitude)),
                    oat_c,
                    # of 1 significant digits
                    abs_tol=10**-1,
                )
            )

            self.assertTrue(
                math.isclose(
                    c_to_f(metric_standard_temperature(altitude)),
                    oat_f,
                    # of 1 significant digits
                    abs_tol=10**-1,
                )
            )

    def test_density_altitude(self):
        # This test ensures that density_altitude works properly with metric
        # values.
        for i in range(20):
            altitude = i * 1000

            self.assertTrue(
                math.isclose(
                    density_altitude(
                        altitude, c_to_f(metric_standard_temperature(altitude))
                    ),
                    altitude,
                    # of 0 significant digits
                    abs_tol=10**-0,
                )
            )


if __name__ == "__main__":
    unittest.main()
