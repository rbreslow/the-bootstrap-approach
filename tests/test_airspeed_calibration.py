import unittest

from examples.n51sw_dataplate import N51SW
from the_bootstrap_approach.airspeed_calibration import (
    cas_to_ias,
    ias_to_cas,
    check_strictly_increasing,
)


class TestAirspeedCalibration(unittest.TestCase):
    def setUp(self):
        # Utilize the airspeed calibration chart from the Dakota POH [6, Fig. 5-1].
        self.dataplate = N51SW

        # Airspeed limitations from the Dakota POH in CAS [6, p. 41].
        self.maneuvering_3000_cas = 122
        self.maneuvering_1761_cas = 94
        self.never_exceed_cas = 171
        self.maximum_structural_cruising_cas = 135
        self.flaps_extended_cas = 100

        # Airspeed limitations from the Dakota POH in IAS.
        self.maneuvering_3000_ias = 124
        self.maneuvering_1761_ias = 96
        self.never_exceed_ias = 173
        self.maximum_structural_cruising_ias = 137
        self.flaps_extended_ias = 102

        pass

    def test_check_strictly_increasing(self):
        self.assertEqual(check_strictly_increasing([1, 2, 3, 4]), [1, 2, 3, 4])
        with self.assertRaises(ValueError):
            check_strictly_increasing([4, 3, 2, 1])

    def test_cas_to_ias(self):
        self.assertEqual(
            cas_to_ias(self.dataplate, self.maneuvering_3000_cas),
            self.maneuvering_3000_ias,
        )
        self.assertEqual(
            cas_to_ias(self.dataplate, self.maneuvering_1761_cas),
            self.maneuvering_1761_ias,
        )
        self.assertEqual(
            cas_to_ias(self.dataplate, self.never_exceed_cas), self.never_exceed_ias
        )
        self.assertEqual(
            cas_to_ias(self.dataplate, self.maximum_structural_cruising_cas),
            self.maximum_structural_cruising_ias,
        )
        self.assertEqual(
            cas_to_ias(self.dataplate, self.flaps_extended_cas), self.flaps_extended_ias
        )

    def test_ias_to_cas(self):
        self.assertEqual(
            ias_to_cas(self.dataplate, self.maneuvering_3000_ias),
            self.maneuvering_3000_cas,
        )
        self.assertEqual(
            ias_to_cas(self.dataplate, self.maneuvering_1761_ias),
            self.maneuvering_1761_cas,
        )
        self.assertEqual(
            ias_to_cas(self.dataplate, self.never_exceed_ias), self.never_exceed_cas
        )
        self.assertEqual(
            ias_to_cas(self.dataplate, self.maximum_structural_cruising_ias),
            self.maximum_structural_cruising_cas,
        )
        self.assertEqual(
            ias_to_cas(self.dataplate, self.flaps_extended_ias), self.flaps_extended_cas
        )


if __name__ == "__main__":
    unittest.main()
