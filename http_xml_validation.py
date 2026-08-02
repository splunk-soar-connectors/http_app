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
import re


UNSAFE_XML_DECLARATION = re.compile(r"<!\s*(?:doctype|entity)\b", re.IGNORECASE)


def reject_unsafe_xml_declarations(xml_text: str) -> str:
    """Reject DTD and entity declarations after the response charset is decoded."""
    if UNSAFE_XML_DECLARATION.search(xml_text):
        raise ValueError("XML responses containing document type or entity declarations are not allowed")
    return xml_text
