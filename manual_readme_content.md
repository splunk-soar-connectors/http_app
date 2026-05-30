For security reasons, accessing 127.0.0.1 is not allowed.

This app requires access to port 80(for request send over HTTP) or port 443(for request send over
HTTPS) on your Phantom host(s) in order to function.

**Authentication is carried out in following priority order**

1. Basic Auth (username and password)
1. OAuth Password grants (username, password, oauth token url, client id and client secret)
1. OAuth (oauth token url, client id and client secret)
1. Provided Auth token (auth_token_name, auth_token)

Basic auth is configured using `username`/`password` fields. For Oauth password grants both the `oauth_username` and `oauth_password` fields must be configured.
