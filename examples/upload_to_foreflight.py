"""
Small CLI to create custom ForeFlight performance profiles using Bootstrap Approach data. Requires that you extract
cookies from a plan.foreflight.com browser session.
"""

import os
import sys

from examples.dakota_performance.climb_performance import cruise_climb_profile, best_rate_of_climb_profile
from examples.dakota_performance.cruise_performance import sixty_five_percent_power_thence_wot_profile, \
    best_range_profile
from examples.foreflight_api import get_aircraft, create_profile
from the_bootstrap_approach.equations import british_standard_temperature
from the_bootstrap_approach.performance import INDEX_GPH, INDEX_KTAS, INDEX_ROC, INDEX_KCAS


def fuel_gal_to_lbf(pressure_altitude, gph):
    """Convert gallons per hour of AvGas to pounds per hour, considering temperature variation."""
    # For 100/130 aviation gasoline: Fuel lbf/U.S. gall = 6.077 - 0.00409 x °F.
    # [1, p. 122].
    fuel_lbf_per_gal = 6.077 - 0.00409 * british_standard_temperature(pressure_altitude)
    return gph * fuel_lbf_per_gal


def search_profiles_for_matching_name(aircraft, name):
    """Try to find a profile w/ the same name to update."""
    detailed_performance_profiles = [profile for profile in list(aircraft["profiles"].values()) if
                                     profile["type"] == "Detailed"]
    for profile in detailed_performance_profiles:
        if profile["performanceProfileName"] == name:
            return profile["metadataOid"]

    return None


def create_foreflight_profile(account_uuid, aircraft_oid, aircraft_uuid, performance_profile_name, climb_profile_name,
                              climb_profile, cruise_profile, descent_profile_name, descent_speed_ias, update=True):
    climb_profile_high_index: int = len(climb_profile) - 1
    climb_ceiling: int = int(climb_profile[climb_profile_high_index][0])

    cruise_profile_high_index: int = len(cruise_profile) - 1
    cruise_ceiling: int = int(cruise_profile[cruise_profile_high_index][0])

    aircraft_ceiling: int = min(climb_ceiling, cruise_ceiling)
    aircraft_ceiling_index: int = int(aircraft_ceiling / 1000)

    detailed_performance_model = {
        "cruise": {
            "name": performance_profile_name
        },
        "points": {},
        "descent": {},
        "climb": {},
    }

    for idx, row in enumerate(cruise_profile):
        if row[0] <= aircraft_ceiling:
            detailed_performance_model["points"][int(row[0])] = {
                "descentSpeed_kias": descent_speed_ias,
                "fuelFlow_pph": fuel_gal_to_lbf(row[0], row[INDEX_GPH + 1]),
                "cruiseSpeed_ktas": row[INDEX_KTAS + 1],
                "climbSpeed_kias": climb_profile[idx][INDEX_KCAS + 1],
                "rateOfClimb_fpm": climb_profile[idx][INDEX_ROC + 1],
            }
        else:
            break

    detailed_performance_model["climb"] = {
        "highAlt_ft": aircraft_ceiling,
        "lowAlt_ft": 0,
        "fuelFlowHighAlt_pph": fuel_gal_to_lbf(aircraft_ceiling, climb_profile[aircraft_ceiling_index][INDEX_GPH + 1]),
        "name": climb_profile_name,
        "fuelFlowLowAlt_pph": fuel_gal_to_lbf(0, climb_profile[0][INDEX_GPH + 1]),
    }

    detailed_performance_model["descent"] = {
        "highAlt_ft": climb_ceiling,
        "lowAlt_ft": 0,
        "fuelFlowHighAlt_pph": detailed_performance_model["points"][aircraft_ceiling]["fuelFlow_pph"],
        "name": descent_profile_name,
        "fuelFlowLowAlt_pph": detailed_performance_model["points"][0]["fuelFlow_pph"],
    }

    aircraft = get_aircraft(account_uuid, aircraft_uuid)

    metadata_oid = None
    if update:
        metadata_oid = search_profiles_for_matching_name(aircraft, performance_profile_name)

    create_profile(account_uuid, metadata_oid, aircraft_oid, aircraft_uuid, performance_profile_name,
                   detailed_performance_model)


def main():
    account_uuid = os.getenv("FOREFLIGHT_ACCOUNT_UUID")
    aircraft_oid = os.getenv("FOREFLIGHT_AIRCRAFT_OID")
    aircraft_uuid = os.getenv("FOREFLIGHT_AIRCRAFT_UUID")

    if None in (account_uuid, aircraft_oid, aircraft_uuid):
        raise Exception("You must configure this script via the environment.")

    # for gross_aircraft_weight in (2250, 2500, 2750, 3000):
    #     climb_profile = cruise_climb_profile(gross_aircraft_weight, isa_diff=0)
    #     cruise_profile = sixty_five_percent_power_thence_wot_profile(gross_aircraft_weight, isa_diff=0)
    #
    #     create_foreflight_profile(
    #         account_uuid,
    #         aircraft_oid,
    #         aircraft_uuid,
    #         f"65% Power Thence Full Throttle, Best Power, {gross_aircraft_weight} lbf",
    #         f"100 KIAS Cruise Climb at Best Power",
    #         climb_profile,
    #         cruise_profile,
    #         f"137 KIAS Descent at 65% Power",
    #         137,
    #         update=True
    #     )

    for gross_aircraft_weight in (2250, 2500, 2750, 3000):
        climb_profile = best_rate_of_climb_profile(gross_aircraft_weight, isa_diff=0)
        cruise_profile = best_range_profile(gross_aircraft_weight, isa_diff=0)

        create_foreflight_profile(
            account_uuid,
            aircraft_oid,
            aircraft_uuid,
            f"Best Range, Best Economy, {gross_aircraft_weight} lbf",
            f"Vy Climb at Best Power",
            climb_profile,
            cruise_profile,
            f"137 KIAS Descent at 65% Power",
            137,
            update=True
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
