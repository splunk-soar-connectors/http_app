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
import json
from typing import Optional

import xmltodict
from bs4 import BeautifulSoup
from pydantic import ValidationError
from soar_sdk.exceptions import ActionFailure

from .common import logger
from .schemas import ParsedResponseBody


def process_xml_response(response) -> dict:
    try:
        return xmltodict.parse(response.text)
    except Exception as e:
        raise ActionFailure(f"Unable to parse XML response. Error: {e}") from e


def process_json_response(response) -> dict:
    try:
        return ParsedResponseBody(**response.json())
    except json.JSONDecodeError as e:
        raise ActionFailure(f"Server claimed JSON but failed to parse. Error: {e}") from e
    except ValidationError as e:
        raise ActionFailure(f"Response JSON did not match expected structure. Details: {e}") from e


def process_html_response(response) -> ParsedResponseBody:
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        for element in soup(["script", "style", "footer", "nav"]):
            element.extract()
        error_text_lines = [x.strip() for x in soup.text.split("\n") if x.strip()]
        cleaned_text = "\n".join(error_text_lines)
        data_dict = {"cleaned_html_text": cleaned_text}
        return ParsedResponseBody(**data_dict)

    except Exception as e:
        raise ActionFailure(f"Unable to parse HTML response. Error: {e}") from e


def process_empty_response(content_type) -> dict:
    message = "Response includes a file" if "octet-stream" in content_type else "Empty response body"
    return {"message": message}


def process_text_response(response) -> ParsedResponseBody:
    data_dict = {"raw_text": response.text}
    return ParsedResponseBody(**data_dict)


RESPONSE_HANDLERS = {
    "json": process_json_response,
    "javascript": process_json_response,
    "xml": process_xml_response,
    "html": process_html_response,
}


def parse_headers(headers_str: Optional[str]) -> dict:
    """
    Parses a JSON string of headers into a dictionary.
    Returns an empty dictionary if the input is empty or None.
    Raises ActionFailure on parsing or validation errors.
    """
    if headers_str is None:
        return {}

    try:
        parsed_headers = json.loads(headers_str)

    except json.JSONDecodeError as e:
        error_message = f"Failed to parse headers. Ensure it's a valid JSON object. Error: {e}"
        logger.error(error_message)
        raise ActionFailure(error_message) from e

    if not isinstance(parsed_headers, dict):
        raise ActionFailure("Headers parameter must be a valid JSON object (dictionary).")

    return parsed_headers


def handle_various_response(response):
    """
    Analyzes the response, routes it to the correct parser, and returns both
    the parsed body and a raw text body for the final output.
    """
    content_type = response.headers.get("Content-Type", "").lower()
    if not response.text.strip() or ("application/octet-stream" in content_type):
        return process_empty_response(content_type), ""

    parser = process_text_response
    for key, handler in RESPONSE_HANDLERS.items():
        if key in content_type:
            parser = handler
            break

    parsed_body = parser(response)

    if isinstance(parsed_body, (dict, list)):
        raw_body = json.dumps(parsed_body, indent=4)
    else:
        raw_body = response.text
    return parsed_body, raw_body
