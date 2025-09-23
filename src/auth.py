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
from abc import ABC, abstractmethod
from typing import Optional

import requests
from requests.auth import AuthBase, HTTPBasicAuth
from soar_sdk.exceptions import ActionFailure

from .common import logger


class Authorization(ABC):
    """
    Abstract base class for defining an authentication strategy.

    Each strategy must implement the `create_auth` method, which is responsible
    for preparing the necessary authentication objects and headers for a request.
    """

    @abstractmethod
    def create_auth(self, headers) -> tuple[Optional[AuthBase], dict]:
        """
        Prepares authentication components for an HTTP request.

        Args:
            headers (dict): The initial dictionary of headers for the request.

        Returns:
            Tuple[Optional[AuthBase], dict]: A tuple containing:
                - An optional `requests.auth.AuthBase` object.
                - The updated headers dictionary.
        """
        pass


class BasicAuth(Authorization):
    """
    Implements HTTP Basic Authentication using username and password.
    """

    def __init__(self, asset):
        self.username = asset.username
        self.password = asset.password

    def create_auth(self, headers):
        logger.info("Using HTTP Basic auth to authenticate")
        return (self.username, self.password), headers


class TokenAuth(Authorization):
    """
    Implements authentication using a static token in a specified header.
    """

    def __init__(self, asset):
        self.auth_token_name = asset.auth_token_name
        self.auth_token = asset.auth_token

    def create_auth(self, headers):
        logger.info("Using provided token to authenticate")
        if self.auth_token and self.auth_token_name not in headers:
            headers[self.auth_token_name] = self.auth_token
        return None, headers


class OAuth(Authorization):
    """
    Implements OAuth 2.0 Client Credentials Grant Flow.

    This strategy fetches an access token from a token URL, caches it in the
    app's authentication state, and adds it to the request as a Bearer token.
    """

    def __init__(self, asset, soar_client, actions_manager):
        self.asset = asset
        self.soar = soar_client
        self.state_key = f"oauth_token_{self.soar.get_asset_id()}"
        self.actions_manager = actions_manager

    def _generate_new_token(self):
        """
        Fetches a new OAuth access token and saves it to the app's auth_state.
        """
        logger.info("Fetching new token")
        
        # Check if we have authorization_url (indicates authorization code flow)
        if self.asset.authorization_url:
            return self._handle_authorization_code_flow()
        else:
            return self._handle_client_credentials_flow()

    def _handle_client_credentials_flow(self):
        """
        Implements OAuth 2.0 Client Credentials Grant Flow.
        """
        logger.info("Using Client Credentials flow")
        token_url = self.asset.oauth_token_url
        client_id = self.asset.client_id
        client_secret = self.asset.client_secret
        scope = self.asset.scope

        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        if scope:
            payload["scope"] = scope

        try:
            response = requests.post(token_url, data=payload, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")

        except requests.exceptions.RequestException as e:
            raise ActionFailure(
                f"Error fetching OAuth token from {token_url}. Details: {e}"
            ) from e
        except json.JSONDecodeError as e:
            raise ActionFailure(
                "Error parsing response from server while fetching token"
            ) from e

        if not access_token:
            raise ActionFailure("Access token not found in response body")

        self.actions_manager.auth_state[self.state_key] = access_token
        logger.info("Successfully fetched and saved new OAuth token to auth_state.")
        return access_token

    def _handle_authorization_code_flow(self):
        """
        Implements OAuth 2.0 Authorization Code Grant Flow.
        
        NOTE: This requires user interaction and is complex in SOAR environment.
        """
        logger.info("Using Authorization Code flow")
        
        # Check if we already have an authorization code in auth_state
        auth_code_key = f"oauth_auth_code_{self.soar.get_asset_id()}"
        auth_code = self.actions_manager.auth_state.get(auth_code_key)
        
        if not auth_code:
            # Generate authorization URL for user to visit
            auth_url = self._generate_authorization_url()
            raise ActionFailure(
                f"Authorization Code Flow requires user interaction. "
                f"Please visit this URL to authorize the app: {auth_url}\n"
                f"After authorization, save the 'code' parameter from the callback URL "
                f"to the app's auth_state with key '{auth_code_key}' and retry."
            )
        
        # Exchange authorization code for access token
        return self._exchange_code_for_token(auth_code)

    def _generate_authorization_url(self):
        """
        Generates the authorization URL for user to visit.
        """
        import urllib.parse
        
        params = {
            "response_type": "code",
            "client_id": self.asset.client_id,
            "redirect_uri": self.asset.redirect_uri,
            "scope": self.asset.scope or "",
            "state": f"soar_asset_{self.soar.get_asset_id()}"  # CSRF protection
        }
        
        # Remove empty parameters
        params = {k: v for k, v in params.items() if v}
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.asset.authorization_url}?{query_string}"

    def _exchange_code_for_token(self, auth_code):
        """
        Exchanges authorization code for access token.
        """
        token_url = self.asset.token_endpoint or self.asset.oauth_token_url
        
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.asset.client_id,
            "client_secret": self.asset.client_secret,
            "redirect_uri": self.asset.redirect_uri,
        }

        try:
            response = requests.post(token_url, data=payload, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")

        except requests.exceptions.RequestException as e:
            raise ActionFailure(
                f"Error exchanging auth code for token from {token_url}. Details: {e}"
            ) from e
        except json.JSONDecodeError as e:
            raise ActionFailure(
                "Error parsing token response from server"
            ) from e

        if not access_token:
            raise ActionFailure("Access token not found in token response")

        # Save access token and clear the auth code (one-time use)
        self.actions_manager.auth_state[self.state_key] = access_token
        auth_code_key = f"oauth_auth_code_{self.soar.get_asset_id()}"
        if auth_code_key in self.actions_manager.auth_state:
            del self.actions_manager.auth_state[auth_code_key]
        
        logger.info("Successfully exchanged auth code for access token.")
        return access_token

    def get_token(self, force_new: bool = False) -> str:
        """
        Retrieves a token, either from the cached state or by fetching a new one.

        Args:
            force_new (bool): If True, forces a new token to be fetched,
                              ignoring any cached token.
        """
        logger.info("Fetching access token")
        cached_token = self.actions_manager.auth_state.get(self.state_key)

        if cached_token and not force_new:
            logger.info("Using old token")
            return cached_token

        return self._generate_new_token()

    def create_auth(self, headers: dict) -> tuple[None, dict]:
        logger.info("Using OAuth to authenticate")

        access_token = self.get_token()

        headers["Authorization"] = f"Bearer {access_token}"

        return None, headers


class NoAuth(Authorization):
    """
    Represents an anonymous request with no authentication.
    """

    def __init__(self, asset):
        pass

    def create_auth(self, headers):
        logger.info("No authentication method configured. Making an anonymous request.")
        return None, headers
