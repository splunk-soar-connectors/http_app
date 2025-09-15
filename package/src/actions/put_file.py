from urllib.parse import quote

import requests
import validators
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..asset import Asset
from ..auth import get_auth_method
from ..common import logger


class PutFileParams(Params):
    """Defines the input parameters for the 'Put File' action."""

    host: str = Param(
        description="Hostname/IP with port number to execute command on",
        primary=True,
        cef_types=["host name"],
    )
    vault_id: str = Param(description="Vault ID of file", primary=True, cef_types=["vault id"])
    file_destination: str = Param(
        description="File destination path (exclude filename)",
        primary=True,
        cef_types=["file path"],
    )
    file_name: str = Param(description="Name of the file to be put on endpoint")
    verify_certificate: bool = Param(description="Verify certificates (if using HTTPS)", default=False)


class PutFileOutput(ActionOutput):
    """Defines the structured output for the 'Put File' action."""

    file_sent: str


verbose = "Provide the path to store the file on the file server. For example, <b>/web_storage/test_repo/</b>."


def put_file(params: PutFileParams, soar: SOARClient, asset: Asset) -> PutFileOutput:
    """Put a file from the vault to another location."""
    logger.info("In action handler for: put_file")
    try:
        logger.info(f"Fetching phantom vault details for vault_id: {params.vault_id}")
        if not (attachments := soar.vault.get_attachment(vault_id=params.vault_id)):
            raise ActionFailure(f"File with vault_id '{params.vault_id}' not found in vault.")
        vault_attachment = attachments[0]
        file_name_to_send = params.file_name or vault_attachment.name
        if params.file_name and vault_attachment.name != params.file_name:
            logger.warning(
                f"Provided file_name '{params.file_name}' does not match the name in vault '{vault_attachment.name}'. Using provided name."
            )
        if file_name_to_send in params.file_destination:
            raise ActionFailure("The filename should be excluded from the 'location' (file destination) parameter.")
        with vault_attachment.open() as f:
            base_url = params.host or asset.base_url
            full_url = f"{base_url.rstrip('/')}/{params.file_destination.lstrip('/')}/{quote(file_name_to_send)}"
            if not validators.url(full_url):
                raise ActionFailure(f"Invalid URL constructed: {full_url}")
            auth_strategy = get_auth_method(asset, soar)
            auth_object, final_headers = auth_strategy.create_auth({})
            files_payload = {"file": f}
            query_params = {"file_path": params.file_destination}
            logger.info(f"Uploading file '{file_name_to_send}' to: {full_url}")
            response = requests.post(
                uri=full_url,
                auth=auth_object,
                headers=final_headers,
                params=query_params,
                files=files_payload,
                verify=params.verify_certificate,
                timeout=asset.timeout,
            )
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ActionFailure(f"Failed to upload file to {full_url}. Details: {e}")
    except Exception as e:
        raise ActionFailure(f"An unexpected error occurred. Details: {e}")
    logger.info(f"File successfully uploaded. Server status: {response.status_code}")
    return PutFileOutput(
        file_sent=full_url,
    )
