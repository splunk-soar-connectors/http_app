from soar_sdk.abstract import SOARClient

from ..asset import Asset
from ..common import logger
from ..request_maker import make_request
from ..schemas import BaseHttpOutput, BaseHttpParams


class GetOptionsParams(BaseHttpParams):

    pass


class GetOptionsOutput(BaseHttpOutput):

    pass


def get_options(params: GetOptionsParams, soar: SOARClient, asset: Asset) -> GetOptionsOutput:
    """Perform a REST OPTIONS call to the server."""
    logger.info("In action handler for: get_options")
    return make_request(
        asset=asset,
        soar=soar,
        method="OPTIONS",
        location=params.location,
        headers=params.headers,
        verify=params.verify_certificate,
        output=GetOptionsOutput,
        body=None,
    )
