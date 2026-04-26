import requests

AUTHENTICATION_MISSING_MSG = (
    "Xen Orchestra api_token or username and password not provided."
)


class XOAClientError(Exception):
    pass


class XOAClient:
    DEFAULT_TIMEOUT = 10

    def __init__(
        self,
        api_host,
        username=None,
        password=None,
        token=None,
        timeout: int = DEFAULT_TIMEOUT,
        validate_certs=True,
        use_ssl=True,
    ) -> None:
        proto = "https" if use_ssl else "http"
        self._base_url = f"{proto}://{api_host}/rest/v0"

        self._username = username
        self._password = password
        self._token = token
        self._timeout = self.DEFAULT_TIMEOUT if timeout is None else timeout
        self._validate_certs = validate_certs

        self.session = requests.Session()
        self._configure_auth()
        self.request("GET", "ping")

    def _configure_auth(self) -> None:
        """Configure authentication on the session."""

        if self._token:
            self.session.cookies.update({"authenticationToken": self._token})
        elif self._username and self._password:
            self.session.auth = (self._username, self._password)
        else:
            raise XOAClientError(AUTHENTICATION_MISSING_MSG)

    def _build_url(self, endpoint: str, path=None) -> str:
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        if path:
            url = f"{url}/{str(path).lstrip('/')}"
        return url

    def request(self, method: str, endpoint: str, path=None, params=None, body=None):
        """Handle all HTTP requests."""

        url = self._build_url(endpoint, path)

        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-type"] = "application/json"

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=body,
                headers=headers,
                timeout=self._timeout,
                verify=self._validate_certs,
            )
        except requests.exceptions.RequestException as exc:
            raise XOAClientError(
                f"Request failed for {method.upper()} {url}: {exc}"
            ) from exc

        if response.status_code == 204:
            return None, response.status_code

        try:
            payload = response.json()
        except ValueError as exc:
            raise XOAClientError(
                f"Expected JSON response for {method.upper()} {url}, got non-JSON body "
                f"with status {response.status_code}"
            ) from exc

        return payload, response.status_code

    def delete(self, endpoint: str, path=None, params=None, body=None):
        return self.request(
            method="DELETE", endpoint=endpoint, path=path, params=params, body=body
        )

    def get(self, endpoint: str, path=None, params=None, body=None):
        return self.request(
            method="GET", endpoint=endpoint, path=path, params=params, body=body
        )

    def post(self, endpoint: str, path=None, params=None, body=None):
        return self.request(
            method="POST", endpoint=endpoint, path=path, params=params, body=body
        )

    def put(self, endpoint: str, path=None, params=None, body=None):
        return self.request(
            method="PUT", endpoint=endpoint, path=path, params=params, body=body
        )
