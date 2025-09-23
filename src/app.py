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
from soar_sdk.app import App

from .actions import (
    action_delete,
    action_get,
    action_head,
    action_options,
    action_patch,
    action_post,
    action_put,
    get_file,
    put_file,
)
from .asset import Asset
from .common import logger
from .schemas import EmptyOutput
from .auth import BasicAuth, TokenAuth, OAuth, NoAuth
from .request_maker import make_request
from soar_sdk.webhooks.models import WebhookRequest, WebhookResponse

app = App(
    name="HTTP",
    app_type="generic",
    logo="logo.svg",
    logo_dark="logo_dark.svg",
    product_vendor="Generic",
    product_name="HTTP",
    publisher="Splunk",
    appid="290b7499-0374-4930-9cdc-5e9b05d65827",
    fips_compliant=False,
    asset_cls=Asset,
)


@app.test_connectivity()
def test_connectivity(soar: SOARClient, asset: Asset) -> None:
    """Validate connection using the configured credentials."""

    logger.info("In action handler for: test_connectivity")

    make_request(
        asset=asset,
        soar=soar,
        method=asset.test_http_method,
        location=asset.test_path if asset.test_path else "",
        output=EmptyOutput,
        verify=False,
        headers=None,
        body=None,
    )

    logger.info("Test connectivity passed!")
    
@app.webhook()
def oauth_callback(WebhookRequest[Asset], asset_id: str) -> WebhookResponse:
    """
    Handle OAuth callback from the OAuth provider.
    """
    logger.info("In action handler for: oauth_callback")
    pass


app.register_action(action_get.get_data, action_type="investigate")
app.register_action(action_post.post_data, action_type="generic", read_only=False)
app.register_action(action_put.put_data, action_type="generic", read_only=False)
app.register_action(action_patch.patch_data, action_type="generic", read_only=False)
app.register_action(action_delete.delete_data, action_type="generic", read_only=False)
app.register_action(action_head.get_headers, action_type="investigate")
app.register_action(action_options.get_options, action_type="investigate")
app.register_action(
    put_file.put_file, action_type="generic", read_only=False, verbose=put_file.VERBOSE
)
app.register_action(
    get_file.get_file, action_type="investigate", verbose=get_file.VERBOSE
)


def get_auth_method(asset: Asset, soar_client: SOARClient):
    """
    Factory function to select and instantiate the appropriate auth strategy.

    Based on the provided asset configuration, this function determines which
    authentication method to use (Basic, Token, OAuth, or None) and returns
    an instance of the corresponding strategy class.
    """
    if asset.username and asset.password:
        return BasicAuth(asset)
    elif asset.auth_token_name and asset.auth_token:
        return TokenAuth(asset)
    elif asset.oauth_token_url and asset.client_id:
        return OAuth(asset, soar_client, app.actions_manager)
    return NoAuth(asset)


if __name__ == "__main__":
    app.cli()
