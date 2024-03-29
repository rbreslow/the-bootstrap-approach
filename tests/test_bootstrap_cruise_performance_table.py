import unittest
import math

from the_bootstrap_approach.conditions import PartialThrottleConditions
from the_bootstrap_approach.dataplate import DataPlate
from the_bootstrap_approach.equations import british_standard_temperature
from the_bootstrap_approach.mixture import Mixture
from the_bootstrap_approach.performance import (
    bootstrap_cruise_performance_table,
    ByKCASRowIndex,
)


class TestBootstrapCruisePerformanceTable(unittest.TestCase):
    def setUp(self):
        # N4697K
        self.dataplate = DataPlate(
            # Airplane configuration. e.g., flaps/gear position.
            "Flaps/Gear Up/Up",
            # S, reference wing area (ft^2).
            174,
            # B, wing span (ft).
            36,
            # C_{D0}, parasite drag coefficient (depends on flaps/gear configuration).
            0.02874,
            # e, airplane efficiency factor (possibly depends on flaps configuration).
            0.7200,
            # P_0, rated MSL shaft power at rated RPM.
            235,
            # N_0, rated MSL full-throttle RPM.
            2400,
            # C, engine power altitude dropoff parameter, the porportion of indicated
            # power that goes to engine friction losses (close to 0.12).
            0.12,
            # c, brake specific full consumption rate (lbm/HP/HR).
            (0.480, 0.430, 0.500),
            # d, propeller diameter (ft).
            6.83,
            # BAF, blade activity factor.
            97.95,
            # Z, ratio of fuselage diameter (taken one propeller diameter behind the
            # propeller) to propeller diameter.
            0.688,
        )

        self.operating_conditions = PartialThrottleConditions(
            self.dataplate,
            3100,
            8000,
            british_standard_temperature(8000),
            Mixture.BEST_POWER,
            2300,
            235 * 0.65 * 550,
        )

        self.table = bootstrap_cruise_performance_table(
            self.dataplate, self.operating_conditions, 60, 180, 0.5
        )

        pass

    def test_ktas(self):
        self.assertTrue(
            math.isclose(
                self.table[0][ByKCASRowIndex.KTAS],
                67.6,
                # of 1 significant digits
                abs_tol=10**-1,
            )
        )

    def test_propeller_efficiency(self):
        self.assertTrue(
            math.isclose(
                self.table[0][ByKCASRowIndex.PROPELLER_EFFICIENCY],
                0.6166,
                # of 4 significant digits
                abs_tol=10**-4,
            )
        )

    def test_thrust(self):
        self.assertTrue(
            math.isclose(
                self.table[0][ByKCASRowIndex.THRUST],
                453,
                # of 0 significant digits
                abs_tol=10**-0,
            )
        )

    def test_drag(self):
        self.assertTrue(
            math.isclose(
                self.table[0][ByKCASRowIndex.DRAG],
                329,
                # of 0 significant digits
                abs_tol=10**-0,
            )
        )

    def test_rate_of_climb(self):
        self.assertTrue(
            math.isclose(
                self.table[0][ByKCASRowIndex.RATE_OF_CLIMB],
                273.2,
                # of 0 significant digits
                abs_tol=10**-0,
            )
        )

    def test_angle_of_climb(self):
        self.assertTrue(
            math.isclose(
                self.table[0][ByKCASRowIndex.ANGLE_OF_CLIMB],
                2.28,
                # of 2 significant digits
                abs_tol=10**-2,
            )
        )


if __name__ == "__main__":
    unittest.main()
