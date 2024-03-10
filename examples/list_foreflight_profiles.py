import os
import sys
from uuid import UUID

from examples.foreflight_api import get_aircraft


def main() -> int:
    account_uuid: UUID = UUID(os.getenv("FOREFLIGHT_ACCOUNT_UUID"))
    aircraft_uuid: UUID = UUID(os.getenv("FOREFLIGHT_AIRCRAFT_UUID"))

    if None in (account_uuid, aircraft_uuid):
        raise Exception("You must configure this script via the environment.")

    # Note: If your session cookie is expired ForeFlight may return a 500 error.
    # We've yet to handle this state.
    aircraft = get_aircraft(account_uuid, aircraft_uuid)

    detailed_performance_profiles = [
        profile
        for profile in list(aircraft["profiles"].values())
        if profile["type"] == "Detailed"
    ]

    for profile in detailed_performance_profiles:
        print(profile["performanceProfileName"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
