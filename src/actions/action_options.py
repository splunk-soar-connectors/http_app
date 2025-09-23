# Copyright (c) 2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from soar_sdk.abstract import SOARClient

from ..asset import Asset
from ..common import logger
from ..request_maker import make_request
from ..schemas import BaseHttpOutput, BaseHttpParams


class GetOptionsParams(BaseHttpParams):
    pass


class GetOptionsOutput(BaseHttpOutput):
    pass


def get_options(
    params: GetOptionsParams, soar: SOARClient, asset: Asset
) -> GetOptionsOutput:
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
