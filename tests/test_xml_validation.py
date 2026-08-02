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
import pytest

from http_xml_validation import reject_unsafe_xml_declarations


def test_reject_unsafe_xml_declarations_accepts_plain_xml():
    xml = "<?xml version='1.0'?><response><status>ok</status></response>"
    assert reject_unsafe_xml_declarations(xml) == xml


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16", "utf-32"])
def test_reject_unsafe_xml_declarations_after_charset_decoding(encoding):
    xml = "<?xml version='1.0'?><!DOCTYPE r [<!ENTITY a 'value'>]><r attr='&a;'/>"
    decoded = xml.encode(encoding).decode(encoding)
    with pytest.raises(ValueError):
        reject_unsafe_xml_declarations(decoded)


@pytest.mark.parametrize("declaration", ["<!doctype r>", "<!DoCtYpE r>", "<!ENTITY a 'value'>", "<! entity a 'value'>"])
def test_reject_unsafe_xml_declarations_rejects_declaration_variants(declaration):
    with pytest.raises(ValueError):
        reject_unsafe_xml_declarations(f"{declaration}<r/>")
