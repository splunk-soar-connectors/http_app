from soar_sdk.abstract import SOARClient
from soar_sdk.params import Param

from ..asset import Asset
from ..common import logger
from ..request_maker import make_request
from ..schemas import BaseHttpOutput, BaseHttpParams


class PostDataOutput(BaseHttpOutput):

    pass


class PostDataParams(BaseHttpParams):

    body: str = Param(description="POST body (query string, JSON, etc.)", required=False)


def post_data(params: PostDataParams, soar: SOARClient, asset: Asset) -> PostDataOutput:
    """Perform a REST POST call to the server."""
    logger.info("In action handler for: http_post")
    return make_request(
        asset=asset,
        soar=soar,
        method="POST",
        location=params.location,
        headers=params.headers,
        verify=params.verify_certificate,
        body=params.body,
        output=PostDataOutput,
    )
