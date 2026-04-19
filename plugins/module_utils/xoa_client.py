import requests

AUTHENTICATION_MISSING_MSG = (
    "Xen Orchestra api_token or username and password not provided."
)


class XOAClient:
    CALL_TIMEOUT = 10

    def __init__(
        self,
        api_host,
        username=None,
        password=None,
        token=None,
        timeout: int = 10,
        validate_certs=True,
        use_ssl=True,
    ) -> None:
        proto = "https" if use_ssl else "http"
        self._base_url = f"{proto}://{api_host}/rest/v0"

        self._username = username
        self._password = password
        self._token = token
        self._timeout = timeout
        self._validate_certs = validate_certs
        self._use_ssl = use_ssl

        self.session = requests.Session()
        self.__set_auth()

    def __set_auth(self) -> None:
        """Sets authorization header or auth based on input."""

        if self._token:
            self.session.cookies.update({"authenticationToken": self._token})
        elif self._username and self._password:
            self.session.auth = (f"{self._username}", f"{self._password}")
        else:
            raise Exception(AUTHENTICATION_MISSING_MSG)

        self.get("ping")

    def _request(self, method: str, endpoint: str, path=None, params=None, body=None):
        """Internal helper to handle all requests."""

        url = f"{self._base_url}/{endpoint.lstrip('/')}"

        if path:
            url = f"{url}/{path.lstrip('/')}"

        if body:
            self.session.headers.update({"Content-type": "application/json"})

        self.session.headers.update({"Accept": "application/json"})

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=body,
                timeout=self._timeout,
                verify=self._validate_certs,
            )

            if response.status_code == 204:
                return None, response.status_code

            return response.json(), response.status_code

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def delete(self, endpoint: str, path=None, params=None, body=None):
        return self._request(
            method="DELETE", endpoint=endpoint, path=path, params=params, body=body
        )

    def get(self, endpoint: str, path=None, params=None, body=None):
        return self._request(
            method="GET", endpoint=endpoint, path=path, params=params, body=body
        )

    def post(self, endpoint: str, path=None, params=None, body=None):
        return self._request(
            method="POST", endpoint=endpoint, path=path, params=params, body=body
        )

    def put(self, endpoint: str, path=None, params=None, body=None):
        return self._request(
            method="PUT", endpoint=endpoint, path=path, params=params, body=body
        )
