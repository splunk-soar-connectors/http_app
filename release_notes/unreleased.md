**Unreleased**

* - Updated connector development tooling.
* Prevented file actions from sending asset credentials to caller-selected hosts.
* Blocked IPv4 and IPv6 loopback or unspecified addresses for asset and file-action URLs.
* Stored downloaded content in a generated temporary file so encoded path separators cannot escape the vault staging directory.
* Enabled TLS certificate verification by default for asset and action requests. Existing assets retain their saved setting and should be reviewed after upgrade.
