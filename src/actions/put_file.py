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
from urllib.parse import quote

import requests
import validators
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params
from ..schemas import PutFileSummary
from ..asset import Asset
from ..common import logger

VERBOSE = "Provide the path to store the file on the file server. For example, <b>/web_storage/test_repo/</b>."


class PutFileParams(Params):
    host: str = Param(
        description="Hostname/IP with port number to execute command on",
        primary=True,
        cef_types=["host name"],
        required=False,
    )
    vault_id: str = Param(
        description="Vault ID of file",
        primary=True,
        cef_types=["vault id"],
        required=True,
    )
    file_destination: str = Param(
        description="File destination path (exclude filename)",
        primary=True,
        cef_types=["file path"],
        required=True,
    )
    file_name: str = Param(
        description="Name of the file to be put on endpoint", required=False
    )
    verify_certificate: bool = Param(
        description="Verify certificates (if using HTTPS)",
        default=False,
        required=False,
    )


class PutFileOutput(ActionOutput):
    file_sent: str


def put_file(params: PutFileParams, soar: SOARClient, asset: Asset) -> PutFileOutput:
    """Put a file from the vault to another location."""
    logger.info("In action handler for: put_file")
    try:
        logger.info(f"Fetching phantom vault details for vault_id: {params.vault_id}")
        if not (attachments := soar.vault.get_attachment(vault_id=params.vault_id)):
            raise ActionFailure(
                f"File with vault_id '{params.vault_id}' not found in vault."
            )
        vault_attachment = attachments[0]
        file_name_to_send = params.file_name or vault_attachment.name
        if params.file_name and vault_attachment.name != params.file_name:
            logger.warning(
                f"Provided file_name '{params.file_name}' does not match the name in vault '{vault_attachment.name}'. Using provided name."
            )
        if file_name_to_send in params.file_destination:
            raise ActionFailure(
                "The filename should be excluded from the 'location' (file destination) parameter."
            )

        base_url = params.host or asset.base_url

        # Handle root directory case
        destination_path = params.file_destination.lstrip("/")
        if destination_path:
            full_url = (
                f"{base_url.rstrip('/')}/{destination_path}/{quote(file_name_to_send)}"
            )
        else:
            full_url = f"{base_url.rstrip('/')}/{quote(file_name_to_send)}"

        if not validators.url(full_url):
            raise ActionFailure(f"Invalid URL constructed: {full_url}")

        with vault_attachment.open("rb") as f:
            from ..app import get_auth_method

            auth_strategy = get_auth_method(asset, soar)
            auth_object, final_headers = auth_strategy.create_auth({})
            files_payload = {"file": f}
            query_params = {"file_path": params.file_destination}
            logger.info(f"Uploading file '{file_name_to_send}' to: {full_url}")
            response = requests.post(
                full_url,
                auth=auth_object,
                headers=final_headers,
                params=query_params,
                files=files_payload,
                verify=params.verify_certificate,
                timeout=asset.timeout,
            )
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ActionFailure(f"Failed to upload file to {full_url}. Details: {e}") from e
    except Exception as e:
        raise ActionFailure(f"An unexpected error occurred. Details: {e}") from e
    logger.info(f"File successfully uploaded. Server status: {response.status_code}")
    put_summary = PutFileSummary(file_sent=full_url)
    soar.set_summary(put_summary)
    soar.set_message(put_summary.get_message())
    return PutFileOutput(
        file_sent=full_url,
    )
