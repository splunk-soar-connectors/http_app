from soar_sdk.abstract import SOARClient
from soar_sdk.params import Param

from ..asset import Asset
from ..common import logger
from ..request_maker import make_request
from ..schemas import BaseHttpOutput, BaseHttpParams

action_type = "generic"


class PatchDataParams(BaseHttpParams):

    body: str = Param(description="PATCH body (query string, JSON, etc.)", required=False)


class PatchDataOutput(BaseHttpOutput):

    pass


def patch_data(params: PatchDataParams, soar: SOARClient, asset: Asset) -> PatchDataOutput:
    """Perform a REST PATCH call to the server."""
    logger.info("In action handler for: patch_data")
    return make_request(
        asset=asset,
        soar=soar,
        method="PATCH",
        location=params.location,
        headers=params.headers,
        verify=params.verify_certificate,
        output=PatchDataOutput,
        body=None,
    )
