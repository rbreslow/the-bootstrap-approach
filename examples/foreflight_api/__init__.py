import json
import os
from typing import Any, Optional
from uuid import UUID

import requests as requests

cookies = {
    "ffsession": os.getenv("FOREFLIGHT_COOKIE_FFSESSION")
}

if None in (cookies["ffsession"],):
    raise Exception(
        "You must configure ForeFlight session cookies via the environment."
    )


def create_profile(
    account_uuid: UUID,
    metadata_oid: str,
    aircraft_oid: str,
    aircraft_uuid: UUID,
    performance_profile_name: str,
    detailed_performance_model: dict[str, Any],
) -> None:
    try:
        response = requests.post(
            url=f"https://plan.foreflight.com/api/1/aircraft/performance/custom/{account_uuid}",  # noqa
            cookies=cookies,
            data=json.dumps(
                {
                    "metadataOid": metadata_oid,
                    "type": "Detailed",
                    "performanceProfileName": performance_profile_name,
                    "aircraftOid": aircraft_oid,
                    "aircraftUUID": str(aircraft_uuid),
                    "climbProfileUUID": None,
                    "performanceProfileClimbName": None,
                    "cruiseProfileUUID": None,
                    "cruiseModelType": None,
                    "descentProfileUUID": None,
                    "performanceProfileDescentName": None,
                    "modelBias": None,
                    "basicPerformanceModel": None,
                    "detailedPerformanceModel": detailed_performance_model,
                    "inSync": True,
                    "foreFlightType": False,
                }
            ),
        )
        print(f"Response HTTP Status Code: {response.status_code}")
        print(f"Response HTTP Response Body: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")


def get_aircraft(account_uuid: UUID, aircraft_uuid: UUID) -> Optional[dict[str, Any]]:
    try:
        response = requests.get(
            # other documented url params:
            # - withLastFlightDate=true
            # - includeSharedObjects=true
            # - withFieldPerfModels=true
            url=f"https://plan.foreflight.com/api/1/aircraft?with_profiles=true&accountUuid={account_uuid}",  # noqa
            cookies=cookies,
        )

        data = response.json()

        # If you've ever received a shared flight plan from someone (e.g., your
        # buddy or flight instructor) then you'll have multiple aircraft with
        # the same UUID. So, you need to filter by account UUID as well.
        search = [
            aircraft
            for aircraft in data["aircraft"]
            if UUID(aircraft["accountUuid"]) == account_uuid
            and UUID(aircraft["aircraftUUID"]) == aircraft_uuid
        ]
        # There should only be one aircraft in your account with the same tail
        # number.
        assert len(search) == 1

        return search[0]
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
