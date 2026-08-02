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
import unittest

from http_xml_validation import reject_unsafe_xml_declarations


class RejectUnsafeXmlDeclarationsTest(unittest.TestCase):
    def test_accepts_plain_xml(self):
        xml = "<?xml version='1.0'?><response><status>ok</status></response>"
        self.assertEqual(reject_unsafe_xml_declarations(xml), xml)

    def test_rejects_after_charset_decoding(self):
        xml = "<?xml version='1.0'?><!DOCTYPE r [<!ENTITY a 'value'>]><r attr='&a;'/>"
        for encoding in ("utf-8", "utf-16", "utf-32"):
            with self.subTest(encoding=encoding), self.assertRaises(ValueError):
                reject_unsafe_xml_declarations(xml.encode(encoding).decode(encoding))

    def test_rejects_declaration_variants(self):
        declarations = ("<!doctype r>", "<!DoCtYpE r>", "<!ENTITY a 'value'>", "<! entity a 'value'>")
        for declaration in declarations:
            with self.subTest(declaration=declaration), self.assertRaises(ValueError):
                reject_unsafe_xml_declarations(f"{declaration}<r/>")
