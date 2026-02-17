For security reasons, accessing 127.0.0.1 is not allowed.

This app requires access to port 80(for request send over HTTP) or port 443(for request send over
HTTPS) on your Phantom host(s) in order to function.

**Authentication is carried out in following priority order**

1. Basic Auth (username and password)
1. OAuth (oauth token url, client id and client secret)
1. Provided Auth token (auth_token_name, auth_token)

### OAuth token request behavior

OAuth mode is used when `oauth_token_url` and `client_id` are configured.

By default, the connector requests tokens using HTTP Basic auth (`client_id` and `client_secret`) and `grant_type=client_credentials` in the request body.

When any of these are provided, client credentials are sent in the request body instead of HTTP Basic auth:

- `oauth_grant_type` set to a value other than `client_credentials`
- `oauth_scope`
- `oauth_resource`
- `oauth_extra_body`

`oauth_extra_body` must be a JSON object string (for example, `{"audience":"https://api.example.com"}`). If duplicated keys are present, `oauth_grant_type`, `oauth_scope`, and `oauth_resource` take precedence over `oauth_extra_body`.
