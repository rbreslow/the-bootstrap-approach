"""
Small CLI to create custom ForeFlight performance profiles using Bootstrap
Approach data. Requires that you extract cookies from a plan.foreflight.com
browser session.
"""
import os
import sys
from typing import Optional, Any
from uuid import UUID

import numpy as np
import numpy.typing as npt

from examples.dakota_performance import cruise_climb, sixty_five_percent_power
from examples.dakota_performance.best_range import best_range
from examples.foreflight_api import get_aircraft, create_profile
from examples.n51sw_dataplate import N51SW
from the_bootstrap_approach.equations import (
    british_standard_temperature,
    fuel_gal_to_lbf,
)
from the_bootstrap_approach.mixture import Mixture
from the_bootstrap_approach.performance import ByAltitudeRowIndex, PerformanceProfile


def search_profiles_for_matching_name(
    aircraft: dict[str, Any], name: str
) -> Optional[str]:
    """Try to find a profile w/ the same name to update."""
    detailed_performance_profiles = [
        profile
        for profile in list(aircraft["profiles"].values())
        if profile["type"] == "Detailed"
    ]
    for profile in detailed_performance_profiles:
        if profile["performanceProfileName"] == name:
            return profile["metadataOid"]

    return None


def create_foreflight_profile(
    account_uuid: UUID,
    aircraft_oid: str,
    aircraft_uuid: UUID,
    performance_profile_name: str,
    climb_profile_name: str,
    climb_profile: npt.NDArray[npt.NDArray[np.float64]],
    cruise_profile: npt.NDArray[npt.NDArray[np.float64]],
    descent_profile_name: str,
    descent_speed_ias: int,
) -> None:
    climb_profile_high_index: int = len(climb_profile) - 1
    climb_ceiling: float = climb_profile[climb_profile_high_index][
        ByAltitudeRowIndex.PRESSURE_ALTITUDE
    ]

    cruise_profile_high_index: int = len(cruise_profile) - 1
    cruise_ceiling: float = cruise_profile[cruise_profile_high_index][
        ByAltitudeRowIndex.PRESSURE_ALTITUDE
    ]

    aircraft_ceiling: float = min(climb_ceiling, cruise_ceiling)
    aircraft_ceiling_index: int = int(aircraft_ceiling / 1000)

    detailed_performance_model: dict[str, Any] = {
        "cruise": {"name": performance_profile_name},
        "points": {},
        "descent": {},
        "climb": {},
    }

    for (
        cruise_row,
        climb_row,
    ) in zip(cruise_profile, climb_profile):
        pressure_altitude = cruise_row[ByAltitudeRowIndex.PRESSURE_ALTITUDE]

        if pressure_altitude <= aircraft_ceiling:
            detailed_performance_model["points"][pressure_altitude] = {
                "descentSpeed_kias": descent_speed_ias,
                "fuelFlow_pph": fuel_gal_to_lbf(
                    cruise_row[ByAltitudeRowIndex.GPH],
                    british_standard_temperature(pressure_altitude),
                ),
                "cruiseSpeed_ktas": cruise_row[ByAltitudeRowIndex.KTAS],
                "climbSpeed_kias": climb_row[ByAltitudeRowIndex.KCAS],
                "rateOfClimb_fpm": climb_row[ByAltitudeRowIndex.RATE_OF_CLIMB],
            }
        else:
            break

    detailed_performance_model["climb"] = {
        "highAlt_ft": aircraft_ceiling,
        "lowAlt_ft": 0,
        "fuelFlowHighAlt_pph": fuel_gal_to_lbf(
            climb_profile[aircraft_ceiling_index][ByAltitudeRowIndex.GPH],
            british_standard_temperature(aircraft_ceiling),
        ),
        "name": climb_profile_name,
        "fuelFlowLowAlt_pph": fuel_gal_to_lbf(
            climb_profile[0][ByAltitudeRowIndex.GPH], british_standard_temperature(0)
        ),
    }

    detailed_performance_model["descent"] = {
        "highAlt_ft": climb_ceiling,
        "lowAlt_ft": 0,
        "fuelFlowHighAlt_pph": detailed_performance_model["points"][aircraft_ceiling][
            "fuelFlow_pph"
        ],
        "name": descent_profile_name,
        "fuelFlowLowAlt_pph": detailed_performance_model["points"][0]["fuelFlow_pph"],
    }

    aircraft = get_aircraft(account_uuid, aircraft_uuid)

    metadata_oid = search_profiles_for_matching_name(aircraft, performance_profile_name)

    create_profile(
        account_uuid,
        metadata_oid,
        aircraft_oid,
        aircraft_uuid,
        performance_profile_name,
        detailed_performance_model,
    )

    print(
        f"Success! {'Updated' if metadata_oid is not None else 'Created'} {performance_profile_name}.\n"  # noqa
    )


def main() -> int:
    account_uuid: UUID = UUID(os.getenv("FOREFLIGHT_ACCOUNT_UUID"))
    aircraft_oid: str = os.getenv("FOREFLIGHT_AIRCRAFT_OID")
    aircraft_uuid: UUID = UUID(os.getenv("FOREFLIGHT_AIRCRAFT_UUID"))

    if None in (account_uuid, aircraft_oid, aircraft_uuid):
        raise Exception("You must configure this script via the environment.")

    for gross_aircraft_weight in (2250, 2500, 2750, 3000):
        climb_profile: PerformanceProfile = cruise_climb(
            N51SW, gross_aircraft_weight, isa_diff=0
        )
        cruise_profile: PerformanceProfile = sixty_five_percent_power(
            N51SW, gross_aircraft_weight, isa_diff=0, mixture=Mixture.BEST_POWER
        )

        create_foreflight_profile(
            account_uuid,
            aircraft_oid,
            aircraft_uuid,
            f"65% Power Thence Full Throttle, {gross_aircraft_weight} lbf",
            climb_profile.name,
            climb_profile.data,
            cruise_profile.data,
            "137 KIAS Descent at 65% Power",
            137,
        )

    for gross_aircraft_weight in (2250, 2500, 2750):
        climb_profile: PerformanceProfile = cruise_climb(
            N51SW, gross_aircraft_weight, isa_diff=0
        )
        cruise_profile: PerformanceProfile = best_range(
            N51SW, gross_aircraft_weight, isa_diff=0, mixture=Mixture.BEST_ECONOMY
        )

        create_foreflight_profile(
            account_uuid,
            aircraft_oid,
            aircraft_uuid,
            f"Best Range, {gross_aircraft_weight} lbf",
            climb_profile.name,
            climb_profile.data,
            cruise_profile.data,
            "137 KIAS Descent at 65% Power",
            137,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
