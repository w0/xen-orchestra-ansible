from ansible_collections.w0.xen_orchestra.plugins.module_utils.xoa_client import (  # type: ignore
    XOAClient,
)

XOA_CONNECTION_SPEC = dict(
    api_host=dict(type="str", required=True),
    username=dict(type="str", no_log=True),
    password=dict(type="str", no_log=True),
    token=dict(type="str", no_log=True),
    use_ssl=dict(type="bool", default=True),
    validate_certs=dict(type="bool", default=True),
)


def build_xoa_argument_spec(extra_spec=None):
    spec = dict(XOA_CONNECTION_SPEC)
    if extra_spec:
        spec.update(extra_spec)
    return spec


def new_xoa_client(module):
    return XOAClient(
        api_host=module.params["api_host"],
        username=module.params["username"],
        password=module.params["password"],
        token=module.params["token"],
        use_ssl=module.params["use_ssl"],
        validate_certs=module.params["validate_certs"],
    )


def validate_auth(module):
    if module.params["token"]:
        if module.params["username"] or module.params["password"]:
            module.fail_json(msg="Token cannot be used with username or password")
    elif module.params["username"] and module.params["password"]:
        pass
    else:
        module.fail_json(msg="Either token or username/password must be provided")
