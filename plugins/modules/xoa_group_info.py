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

VDI_SUBRESOURCES = {
    "tasks": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "users": {"supported_params": STANDARD_COLLECTION_PARAMS},
}


def _validate_request_shape(module):

    group_uuid = module.params["group_uuid"]
    subresource = module.params["subresource"]

    if subresource and not group_uuid:
        module.fail_json(msg="subresource requires group_uuid")

    if subresource and subresource not in VDI_SUBRESOURCES:
        module.fail_json(msg=f"Invalid subresource: {subresource}")

    provided = provided_optional_params(module)
    allowed = allowed_request_parameters(VDI_SUBRESOURCES, group_uuid, subresource)

    if not group_uuid:
        allowed = STANDARD_COLLECTION_PARAMS
        label = "group collection request"
    elif not subresource:
        allowed = set()
        label = "group detail request"
    else:
        allowed = VDI_SUBRESOURCES[subresource]["supported_params"]
        label = f"group subresource '{subresource}'"

    fail_on_unsupported_params(module, provided, allowed, label)


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            group_uuid=dict(type="str"),
            subresource=dict(type="str", choices=list(VDI_SUBRESOURCES.keys())),
            fields=dict(type="list", elements="str"),
            filter=dict(type="list", elements="str"),
            limit=dict(type="int"),
            ndjson=dict(type="bool"),
            markdown=dict(type="bool"),
        )
    )

    validate_auth(module)
    _validate_request_shape(module)

    path = build_resource_path(module.params["group_uuid"], module.params["subresource"])
    params = build_query_params(module)

    try:
        client = new_xoa_client(module)
        response, status_code = client.get("groups", path, params=params)

    except Exception as e:
        module.fail_json(msg=str(e))

    if status_code != 200:
        module.fail_json(msg=f"Unexpected status code: {status_code}")

    module.exit_json(changed=False, result=response)


if __name__ == "__main__":
    main()
