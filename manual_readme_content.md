Initial asset and file-action destinations cannot resolve to loopback or unspecified addresses. Redirects follow Requests' standard handling.

HTTP actions honor the asset's `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` environment variables. The proxy resolves proxied destination names; direct connections validate destination DNS on the SOAR host before dispatch. Configure the proxy to block internal destinations that only the proxy can resolve.

This app requires access to port 80(for request send over HTTP) or port 443(for request send over
HTTPS) on your Phantom host(s) in order to function.

**Authentication is carried out in following priority order**

1. Basic Auth (username and password)
1. OAuth (oauth token url, client id and client secret)
1. Provided Auth token (auth_token_name, auth_token)

### Sensitive response headers

By default, HTTP actions omit `Authorization`, `Cookie`, `Proxy-Authenticate`, `Set-Cookie`, and `Set-Cookie2` from
`response_headers`. Enable `expose_sensitive_response_headers` only for a specific action run that requires these values.

When enabled, the unredacted values are persisted in the container's action results. A user with permission to view that
container can retrieve them later, even if the user did not run the action. Treat these values as credentials or session
material and enable the option only when the workflow requires it.
