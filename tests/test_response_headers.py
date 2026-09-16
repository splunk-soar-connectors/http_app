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

import ast
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTTP_ACTIONS = {"http_delete", "http_get", "http_head", "http_options", "http_patch", "http_post", "http_put"}


def load_safe_response_headers():
    tree = ast.parse((ROOT / "http_connector.py").read_text())
    connector = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "HttpConnector")
    sensitive_headers = next(
        node
        for node in connector.body
        if isinstance(node, ast.Assign) and any(target.id == "SENSITIVE_RESPONSE_HEADERS" for target in node.targets)
    )
    safe_response_headers = next(node for node in connector.body if isinstance(node, ast.FunctionDef) and node.name == "_safe_response_headers")
    class_body = ast.ClassDef(
        name="ResponseHeaders",
        bases=[],
        keywords=[],
        body=[sensitive_headers, safe_response_headers],
        decorator_list=[],
    )
    namespace = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[class_body], type_ignores=[])), "http_connector.py", "exec"), namespace)
    return namespace["ResponseHeaders"]._safe_response_headers


class ResponseHeadersTest(unittest.TestCase):
    def test_sensitive_response_headers_are_filtered_by_default(self):
        safe_response_headers = load_safe_response_headers()

        self.assertEqual(
            safe_response_headers({"Set-Cookie": "session=secret", "X-Request-Id": "request-id"}),
            {"X-Request-Id": "request-id"},
        )

    def test_sensitive_response_headers_are_returned_when_explicitly_enabled(self):
        safe_response_headers = load_safe_response_headers()
        headers = {"Set-Cookie": "session=secret", "Authorization": "Bearer secret", "X-Request-Id": "request-id"}

        self.assertEqual(safe_response_headers(headers, True), headers)

    def test_http_actions_expose_an_opt_in_parameter_with_a_safe_default(self):
        manifest = json.loads((ROOT / "http.json").read_text())
        actions = {action["identifier"]: action for action in manifest["actions"] if action["identifier"] in HTTP_ACTIONS}

        self.assertEqual(set(actions), HTTP_ACTIONS)
        for action in actions.values():
            parameter = action["parameters"]["expose_sensitive_response_headers"]
            self.assertEqual(parameter["data_type"], "boolean")
            self.assertIs(parameter["default"], False)
            self.assertIn("Authorization, Cookie, Proxy-Authenticate, Set-Cookie, and Set-Cookie2", parameter["description"])
            self.assertIn("container viewers", parameter["description"])


if __name__ == "__main__":
    unittest.main()
