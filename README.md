# HTTP

Publisher: Splunk <br>
Connector Version: 4.0.0 <br>
Product Vendor: Generic <br>
Product Name: HTTP <br>
Minimum Product Version: 6.4.0

This App facilitates making HTTP requests as actions

For security reasons, accessing 127.0.0.1 is not allowed.

This app requires access to port 80(for request send over HTTP) or port 443(for request send over
HTTPS) on your Phantom host(s) in order to function.

**Authentication is carried out in following priority order**

1. Basic Auth (username and password)
1. OAuth (oauth token url, client id and client secret)
1. Provided Auth token (auth_token_name, auth_token)

### Configuration variables

This table lists the configuration variables required to operate HTTP. These variables are specified when configuring a HTTP asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**base_url** | required | string | Base URL for making queries. (e.g. https://myservice/) |
**test_path** | optional | string | Endpoint for test connectivity. (e.g. /some/specific/endpoint , appended to Base URL) |
**auth_token_name** | optional | string | Type of authentication token |
**auth_token** | optional | password | Value of authentication token |
**username** | optional | string | Username (for HTTP basic auth) |
**password** | optional | password | Password (for HTTP basic auth) |
**oauth_token_url** | optional | string | URL to fetch oauth token from |
**client_id** | optional | string | Client ID (for OAuth) |
**client_secret** | optional | password | Client Secret (for OAuth) |
**timeout** | optional | numeric | Timeout for HTTP calls |
**test_http_method** | optional | string | HTTP Method for Test Connectivity |

### Supported Actions

[test connectivity](#action-test-connectivity) - Validate connection using the configured credentials. <br>
[get data](#action-get-data) - Perform a REST GET call to the server. <br>
[post data](#action-post-data) - Perform a REST POST call to the server. <br>
[put data](#action-put-data) - Perform a REST PUT call to the server. <br>
[patch data](#action-patch-data) - Perform a REST PATCH call to the server. <br>
[delete data](#action-delete-data) - Perform a REST DELETE call to the server. <br>
[get headers](#action-get-headers) - Perform a REST HEAD call to the server. <br>
[get options](#action-get-options) - Perform a REST OPTIONS call to the server. <br>
[put file](#action-put-file) - Put a file from the vault to another location. <br>
[get file](#action-get-file) - Retrieve a file from the endpoint and save it to the vault.

## action: 'test connectivity'

Validate connection using the configured credentials.

Type: **test** <br>
Read only: **True**

Basic test for app.

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get data'

Perform a REST GET call to the server.

Type: **investigate** <br>
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**location** | required | Location (e.g. path/to/endpoint) | string | `endpoint` |
**verify_certificate** | optional | Verify certificates (if using HTTPS) | boolean | |
**headers** | optional | Additional headers (JSON object with headers) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.location | string | `endpoint` | |
action_result.parameter.verify_certificate | boolean | | |
action_result.parameter.headers | string | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"failed": true, "message": "Requested item not found"} |
action_result.data.\*.location | string | `url` | http://192.168.1.26/rest/assets |
action_result.data.\*.method | string | | POST |
action_result.data.\*.response_headers | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'post data'

Perform a REST POST call to the server.

Type: **generic** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**location** | required | Location (e.g. path/to/endpoint) | string | `endpoint` |
**verify_certificate** | optional | Verify certificates (if using HTTPS) | boolean | |
**headers** | optional | Additional headers (JSON object with headers) | string | |
**body** | optional | POST body (query string, JSON, etc.) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.location | string | `endpoint` | |
action_result.parameter.verify_certificate | boolean | | |
action_result.parameter.headers | string | | |
action_result.parameter.body | string | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"failed": true, "message": "Requested item not found"} |
action_result.data.\*.location | string | `url` | http://192.168.1.26/rest/assets |
action_result.data.\*.method | string | | POST |
action_result.data.\*.response_headers | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'put data'

Perform a REST PUT call to the server.

Type: **generic** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**location** | required | Location (e.g. path/to/endpoint) | string | `endpoint` |
**verify_certificate** | optional | Verify certificates (if using HTTPS) | boolean | |
**headers** | optional | Additional headers (JSON object with headers) | string | |
**body** | optional | PATCH body (query string, JSON, etc.) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.location | string | `endpoint` | |
action_result.parameter.verify_certificate | boolean | | |
action_result.parameter.headers | string | | |
action_result.parameter.body | string | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"failed": true, "message": "Requested item not found"} |
action_result.data.\*.location | string | `url` | http://192.168.1.26/rest/assets |
action_result.data.\*.method | string | | POST |
action_result.data.\*.response_headers | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'patch data'

Perform a REST PATCH call to the server.

Type: **generic** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**location** | required | Location (e.g. path/to/endpoint) | string | `endpoint` |
**verify_certificate** | optional | Verify certificates (if using HTTPS) | boolean | |
**headers** | optional | Additional headers (JSON object with headers) | string | |
**body** | optional | PATCH body (query string, JSON, etc.) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.location | string | `endpoint` | |
action_result.parameter.verify_certificate | boolean | | |
action_result.parameter.headers | string | | |
action_result.parameter.body | string | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"failed": true, "message": "Requested item not found"} |
action_result.data.\*.location | string | `url` | http://192.168.1.26/rest/assets |
action_result.data.\*.method | string | | POST |
action_result.data.\*.response_headers | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'delete data'

Perform a REST DELETE call to the server.

Type: **generic** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**location** | required | Location (e.g. path/to/endpoint) | string | `endpoint` |
**verify_certificate** | optional | Verify certificates (if using HTTPS) | boolean | |
**headers** | optional | Additional headers (JSON object with headers) | string | |
**body** | optional | DELETE body (query string, JSON, etc.) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.location | string | `endpoint` | |
action_result.parameter.verify_certificate | boolean | | |
action_result.parameter.headers | string | | |
action_result.parameter.body | string | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"failed": true, "message": "Requested item not found"} |
action_result.data.\*.location | string | `url` | http://192.168.1.26/rest/assets |
action_result.data.\*.method | string | | POST |
action_result.data.\*.response_headers | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get headers'

Perform a REST HEAD call to the server.

Type: **investigate** <br>
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**location** | required | Location (e.g. path/to/endpoint) | string | `endpoint` |
**verify_certificate** | optional | Verify certificates (if using HTTPS) | boolean | |
**headers** | optional | Additional headers (JSON object with headers) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.location | string | `endpoint` | |
action_result.parameter.verify_certificate | boolean | | |
action_result.parameter.headers | string | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"failed": true, "message": "Requested item not found"} |
action_result.data.\*.location | string | `url` | http://192.168.1.26/rest/assets |
action_result.data.\*.method | string | | POST |
action_result.data.\*.response_headers | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get options'

Perform a REST OPTIONS call to the server.

Type: **investigate** <br>
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**location** | required | Location (e.g. path/to/endpoint) | string | `endpoint` |
**verify_certificate** | optional | Verify certificates (if using HTTPS) | boolean | |
**headers** | optional | Additional headers (JSON object with headers) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.location | string | `endpoint` | |
action_result.parameter.verify_certificate | boolean | | |
action_result.parameter.headers | string | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"failed": true, "message": "Requested item not found"} |
action_result.data.\*.location | string | `url` | http://192.168.1.26/rest/assets |
action_result.data.\*.method | string | | POST |
action_result.data.\*.response_headers | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'put file'

Put a file from the vault to another location.

Type: **generic** <br>
Read only: **False**

Provide the path to store the file on the file server. For example, <b>/web_storage/test_repo/</b>.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**host** | required | Hostname/IP with port number to execute command on | string | `host name` |
**vault_id** | required | Vault ID of file | string | `vault id` |
**file_destination** | required | File destination path (exclude filename) | string | `file path` |
**file_name** | required | Name of the file to be put on endpoint | string | |
**verify_certificate** | required | Verify certificates (if using HTTPS) | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.host | string | `host name` | |
action_result.parameter.vault_id | string | `vault id` | |
action_result.parameter.file_destination | string | `file path` | |
action_result.parameter.file_name | string | | |
action_result.parameter.verify_certificate | boolean | | |
action_result.data.\*.file_sent | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get file'

Retrieve a file from the endpoint and save it to the vault.

Type: **investigate** <br>
Read only: **True**

Provide the file path and file name to download into the vault. For example, <b>/web_storage/file.tgz</b>.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**hostname** | required | Hostname to execute command on | string | `hostname` |
**file_path** | required | Path of the file to download (include filename) | string | `file path` |
**verify_certificate** | required | Verify certificates (if using HTTPS) | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.hostname | string | `hostname` | |
action_result.parameter.file_path | string | `file path` | |
action_result.parameter.verify_certificate | boolean | | |
action_result.data.\*.vault_id | string | | |
action_result.data.\*.file_name | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2025 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
