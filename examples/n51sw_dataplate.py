import numpy as np

from the_bootstrap_approach.dataplate import DataPlate

# These values are from the Dakota POH airspeed calibration chart [6, Fig. 5-1].
dakota_asi_calibration_curve = np.array(
    [
        [55.5, 51.5],
        [56, 52.5],
        [57, 54],
        [60.5, 58.5],
        [61.75, 60.25],
        [68, 68],
        [70, 70.5],
        [74, 75.25],
        [76, 77.5],
        [78, 79.75],
        [80, 82],
        [82, 84],
        [84, 86],
        [86, 88],
        [90, 92],
        [92, 94],
        [94, 96],
        [100, 102],
        [104, 106],
        [106, 108],
        [118, 120],
        [122, 124],
        [135, 137],
        [138, 140],
        [140, 142],
        [158, 160],
        [171, 173],
    ]
)

# As glide tested on December 5th 2021, as Z and BAF determined on December 6th
# 2021, using Piper's provided ASI calibration curves.
N51SW = DataPlate(
    # Airplane configuration. e.g., flaps/gear position.
    "Flaps Up",
    # S, reference wing area (ft^2).
    170,
    # B, wing span (ft).
    425.11 / 12,
    # C_{D0}, parasite drag coefficient (depends on flaps/gear configuration).
    0.0357162948271769,
    # e, airplane efficiency factor (possibly depends on flaps configuration).
    0.673966174425770,
    # P_0, rated MSL shaft power at rated RPM.
    235,
    # N_0, rated MSL full-throttle RPM.
    2400,
    # C, engine power altitude dropoff parameter, the porportion of indicated
    # power that goes to engine friction losses (close to 0.12).
    0.12,
    # c, brake specific full consumption rate (lbm/HP/HR).
    # > Model O-540-J3A5D Engines – Manual leaning is permitted at cruise
    # > conditions up to 85% power resulting in a BSFC of .420 lbs./BHP./hr. at
    # > best economy and .460 lbs./BHP./hr. at best power. Minimum allowable
    # > BSFC at take-off and climb conditions is .500 lbs./BHP./hr.
    (0.460, 0.420, 0.500),
    # d, propeller diameter (ft).
    80 / 12,
    # BAF, blade activity factor.
    101.600808244411,
    # Z, ratio of fuselage diameter (taken one propeller diameter behind the
    # propeller) to propeller diameter.
    ((43 + (5 / 16) + 48) / 2) / 80,
    dakota_asi_calibration_curve,
)
