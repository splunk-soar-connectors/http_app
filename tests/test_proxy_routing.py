# Copyright (c) 2026 Splunk Inc.
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
import importlib.util
import os
import socket
import sys
import threading
import types
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

import requests


def load_connector():
    phantom = types.ModuleType("phantom")
    phantom.__path__ = []
    stubs = {
        name: types.ModuleType(name)
        for name in (
            "encryption_helper",
            "magic",
            "validators",
            "xmltodict",
            "bs4",
            "phantom.app",
            "phantom.rules",
            "phantom.action_result",
            "phantom.base_connector",
            "phantom.vault",
        )
    }
    stubs["bs4"].BeautifulSoup = object
    stubs["bs4"].UnicodeDammit = object
    stubs["phantom.app"].APP_SUCCESS = 0
    stubs["phantom.app"].APP_ERROR = 1
    stubs["phantom.app"].is_fail = lambda status: status != 0
    stubs["phantom.action_result"].ActionResult = object
    stubs["phantom.base_connector"].BaseConnector = object
    stubs["phantom.vault"].Vault = object
    stubs["phantom"] = phantom
    for name, module in stubs.items():
        if name.startswith("phantom."):
            setattr(phantom, name.removeprefix("phantom."), module)

    spec = importlib.util.spec_from_file_location("http_connector_proxy_test", Path(__file__).resolve().parents[1] / "http_connector.py")
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, stubs):
        spec.loader.exec_module(module)
    return module


connector_module = load_connector()


class ActionResult:
    def __init__(self):
        self.data = []
        self.status = 0

    def set_status(self, status, *_args):
        self.status = status
        return status

    def add_data(self, data):
        self.data.append(data)

    def update_summary(self, _summary):
        pass


class ProxyHandler(BaseHTTPRequestHandler):
    requests_seen = []

    def do_GET(self):
        self.requests_seen.append(self.path)
        redirect = {
            "http://first.invalid/redirect": "http://second.invalid/final",
            "http://first.invalid/loopback": "http://127.0.0.1/final",
        }.get(self.path)
        self.send_response(302 if redirect else 200)
        if redirect:
            self.send_header("Location", redirect)
        self.send_header("Content-Length", "0" if redirect else "2")
        self.end_headers()
        if not redirect:
            self.wfile.write(b"ok")

    def log_message(self, *_args):
        pass


class ProxyRoutingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proxy = ThreadingHTTPServer(("127.0.0.1", 0), ProxyHandler)
        cls.thread = threading.Thread(target=cls.proxy.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.proxy.shutdown()
        cls.proxy.server_close()
        cls.thread.join()

    def setUp(self):
        ProxyHandler.requests_seen.clear()
        self.proxy_url = f"http://127.0.0.1:{self.proxy.server_port}"
        self.connector = connector_module.HttpConnector()
        self.connector._base_url = "http://first.invalid"
        self.connector._token_name = "X-Token"
        self.connector._token = "test"
        self.connector._timeout = 3
        self.connector.get_action_identifier = lambda: "http_get"
        self.connector.save_progress = lambda *_args: None
        self.connector._buffer_xml_response = lambda *_args: 0
        self.connector._process_response = lambda response, _result: (0, response.text)

    def test_proxy_resolves_initial_and_redirected_hosts(self):
        real_getaddrinfo = socket.getaddrinfo

        def restricted_dns(host, *args, **kwargs):
            if host.endswith(".invalid"):
                raise socket.gaierror("destination DNS is unavailable")
            return real_getaddrinfo(host, *args, **kwargs)

        with (
            mock.patch.dict(os.environ, {"HTTP_PROXY": self.proxy_url}, clear=True),
            mock.patch.object(connector_module.socket, "getaddrinfo", side_effect=restricted_dns),
        ):
            self.assertIsNone(self.connector._get_url_address_error("http://first.invalid"))
            status, _ = self.connector._make_http_call(ActionResult(), endpoint="/redirect")

        self.assertEqual(status, 0)
        self.assertEqual(ProxyHandler.requests_seen, ["http://first.invalid/redirect", "http://second.invalid/final"])

    def test_redirect_is_not_checked_as_an_initial_destination(self):
        with mock.patch.dict(os.environ, {"HTTP_PROXY": self.proxy_url}, clear=True):
            self.assertIsNone(self.connector._get_url_address_error("http://first.invalid"))
            status, _ = self.connector._make_http_call(ActionResult(), endpoint="/loopback")
        self.assertEqual(status, 0)
        self.assertEqual(ProxyHandler.requests_seen, ["http://first.invalid/loopback", "http://127.0.0.1/final"])

    def test_no_proxy_keeps_direct_initial_destination_validation(self):
        with (
            mock.patch.dict(os.environ, {"HTTP_PROXY": self.proxy_url, "NO_PROXY": "first.invalid"}, clear=True),
            mock.patch.object(connector_module.socket, "getaddrinfo", side_effect=socket.gaierror("DNS unavailable")) as lookup,
        ):
            error = self.connector._get_url_address_error("http://first.invalid")
        self.assertIn("Unable to resolve URL host first.invalid", error)
        lookup.assert_called_once()

    def test_initial_loopback_target_is_rejected(self):
        with mock.patch.dict(os.environ, {"HTTP_PROXY": self.proxy_url}, clear=True):
            self.assertIn("loopback", self.connector._get_url_address_error("http://127.0.0.1"))

    def test_https_proxy_reaches_requests_environment_handling(self):
        response = requests.Response()
        response.status_code = 200
        response._content = b"ok"
        self.connector._base_url = "https://first.invalid"
        with (
            mock.patch.dict(os.environ, {"HTTPS_PROXY": self.proxy_url}, clear=True),
            mock.patch.object(connector_module.socket, "getaddrinfo", side_effect=socket.gaierror("DNS unavailable")) as lookup,
            mock.patch.object(requests.sessions.Session, "send", return_value=response) as send,
        ):
            self.assertIsNone(self.connector._get_url_address_error("https://first.invalid"))
            status, _ = self.connector._make_http_call(ActionResult(), endpoint="/data")
        self.assertEqual(status, 0)
        self.assertEqual(send.call_args.kwargs["proxies"]["https"], self.proxy_url)
        lookup.assert_not_called()


if __name__ == "__main__":
    unittest.main()
