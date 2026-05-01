from ansible.module_utils.basic import AnsibleModule
from ansible_collections.w0.xen_orchestra.plugins.module_utils.xoa import (  # type: ignore
    build_xoa_argument_spec,
    new_xoa_client,
    validate_auth,
)
from ansible_collections.w0.xen_orchestra.plugins.module_utils.xoa_info import (  # type: ignore
    STANDARD_COLLECTION_PARAMS,
    build_query_params,
    build_resource_path,
    fail_on_unsupported_params,
    provided_optional_params,
)


def _validate_request_shape(module):

    pgpu_uuid = module.params["pgpu_uuid"]

    provided = provided_optional_params(module)

    if not pgpu_uuid:
        allowed = STANDARD_COLLECTION_PARAMS
        label = "pgpu collection request"
    else:
        allowed = set()
        label = "pgpu detail request"

    fail_on_unsupported_params(module, provided, allowed, label)


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            pgpu_uuid=dict(type="str"),
            fields=dict(type="list", elements="str"),
            filter=dict(type="list", elements="str"),
            limit=dict(type="int"),
            ndjson=dict(type="bool"),
            markdown=dict(type="bool"),
        )
    )

    validate_auth(module)
    _validate_request_shape(module)

    path = build_resource_path(module.params["pgpu_uuid"], module.params["subresource"])
    params = build_query_params(module)

    try:
        client = new_xoa_client(module)
        response, status_code = client.get("pgpus", path, params=params)

    except Exception as e:
        module.fail_json(msg=str(e))

    if status_code != 200:
        module.fail_json(msg=f"Unexpected status code: {status_code}")

    module.exit_json(changed=False, result=response)


if __name__ == "__main__":
    main()
