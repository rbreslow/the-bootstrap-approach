from typing import Union

import numpy as np
import numpy.typing as npt

from the_bootstrap_approach.dataplate import DataPlate


def check_strictly_increasing(
    coordinate_sequence: npt.NDArray[np.floating],
) -> npt.NDArray[np.floating]:
    # > The x-coordinate sequence is expected to be increasing, but this is not
    # > explicitly enforced. However, if the sequence xp is non-increasing,
    # > interpolation results are meaningless.
    # https://numpy.org/doc/stable/reference/generated/numpy.interp.html
    if not np.all(np.diff(coordinate_sequence) > 0):
        raise ValueError("The coordinate sequence is expected to be increasing.")

    return coordinate_sequence


def cas_to_ias(
    dataplate: DataPlate, cas: Union[float, npt.NDArray[np.floating]]
) -> Union[float, npt.NDArray[np.floating]]:
    """Convert calibrated airspeed to indicated airspeed, using the dataplate's
    calibration curve."""
    if dataplate.asi_calibration_curve is not None:
        x = check_strictly_increasing(dataplate.asi_calibration_curve[:, 0])
        y = check_strictly_increasing(dataplate.asi_calibration_curve[:, 1])

        # Return NaN if we are trying to determine indicated airspeed outside
        # the bounds of the calibration curve.
        return np.interp(cas, x, y, left=np.nan, right=np.nan)
    else:
        # Treat the calibration curve as an optional attribute. If the dataplate
        # doesn't have a calibration curve, we simply return NaN.
        return cas * np.nan


def ias_to_cas(
    dataplate: DataPlate, ias: Union[float, npt.NDArray[np.floating]]
) -> Union[float, npt.NDArray[np.floating]]:
    """Convert indicated airspeed to calibrated airspeed, using the dataplate's
    calibration curve."""
    if dataplate.asi_calibration_curve is not None:
        x = check_strictly_increasing(dataplate.asi_calibration_curve[:, 0])
        y = check_strictly_increasing(dataplate.asi_calibration_curve[:, 1])

        return np.interp(ias, y, x, left=np.nan, right=np.nan)
    else:
        return ias * np.nan
