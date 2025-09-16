from soar_sdk.abstract import SOARClient
from soar_sdk.params import Param

from ..asset import Asset
from ..common import logger
from ..request_maker import make_request
from ..schemas import BaseHttpOutput, BaseHttpParams

action_type = "generic"


class PutDataOutput(BaseHttpOutput):

    pass


class PutDataParams(BaseHttpParams):

    body: str = Param(description="PATCH body (query string, JSON, etc.)", required=False)


def put_data(params: PutDataParams, soar: SOARClient, asset: Asset) -> PutDataOutput:
    """Perform a REST PUT call to the server."""
    logger.info("In action handler for: put_data")
    return make_request(
        asset=asset,
        soar=soar,
        method="PUT",
        location=params.location,
        headers=params.headers,
        verify=params.verify_certificate,
        body=params.body,
        output=PutDataOutput,
    )
