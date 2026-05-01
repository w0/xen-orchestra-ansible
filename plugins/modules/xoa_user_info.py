from ansible.module_utils.basic import AnsibleModule
from ansible_collections.w0.xen_orchestra.plugins.module_utils.xoa import (  # type: ignore
    build_xoa_argument_spec,
    new_xoa_client,
    validate_auth,
)
from ansible_collections.w0.xen_orchestra.plugins.module_utils.xoa_info import (  # type: ignore
    STANDARD_COLLECTION_PARAMS,
    allowed_request_parameters,
    build_query_params,
    build_resource_path,
    fail_on_unsupported_params,
    provided_optional_params,
)

USER_SUBRESOURCES = {
    "acl-privileges": {"supported_params": STANDARD_COLLECTION_PARAMS.remove("markdown")},
    "authentication_tokens": {"supported_params": {"id", "filter", "limit"}},
    "groups": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "tasks": {"supported_params": STANDARD_COLLECTION_PARAMS},
}


def _validate_request_shape(module):

    user_uuid = module.params["user_uuid"]
    subresource = module.params["subresource"]

    if subresource and not user_uuid:
        module.fail_json(msg="subresource requires user_uuid")

    if subresource and subresource not in USER_SUBRESOURCES:
        module.fail_json(msg=f"Invalid subresource: {subresource}")

    provided = provided_optional_params(module)
    allowed = allowed_request_parameters(USER_SUBRESOURCES, user_uuid, subresource)

    if not user_uuid:
        allowed = STANDARD_COLLECTION_PARAMS
        label = "user collection request"
    elif not subresource:
        allowed = set()
        label = "user detail request"
    else:
        allowed = USER_SUBRESOURCES[subresource]["supported_params"]
        label = f"user subresource '{subresource}'"

    fail_on_unsupported_params(module, provided, allowed, label)


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            user_uuid=dict(type="str"),
            subresource=dict(type="str", choices=list(USER_SUBRESOURCES.keys())),
            fields=dict(type="list", elements="str"),
            filter=dict(type="list", elements="str"),
            limit=dict(type="int"),
            ndjson=dict(type="bool"),
            markdown=dict(type="bool"),
        )
    )

    validate_auth(module)
    _validate_request_shape(module)

    path = build_resource_path(module.params["user_uuid"], module.params["subresource"])
    params = build_query_params(module)

    try:
        client = new_xoa_client(module)
        response, status_code = client.get("users", path, params=params)

    except Exception as e:
        module.fail_json(msg=str(e))

    if status_code != 200:
        module.fail_json(msg=f"Unexpected status code: {status_code}")

    module.exit_json(changed=False, result=response)


if __name__ == "__main__":
    main()
