#!/usr/bin/python

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
)

POOL_SUBRESOURCES = {
    "alarms": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "backup-jobs": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "dashboard": {"supported_params": {"ndjson"}},
    "messages": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "missing_patches": {"supported_params": set()},
    "stats": {"supported_params": {"granularity"}},
    "tasks": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "vdis": {"supported_params": STANDARD_COLLECTION_PARAMS},
}


def _provided_optional_params(module):
    """
    Returns the set of optional parameters provided by the user.
    """
    provided = set()

    if module.params["fields"]:
        provided.add("fields")
    if module.params["filter"]:
        provided.add("filter")
    if module.params["limit"] is not None:
        provided.add("limit")
    if module.params["ndjson"] is not None:
        provided.add("ndjson")
    if module.params["markdown"] is not None:
        provided.add("markdown")
    if module.params["granularity"]:
        provided.add("granularity")

    return provided


def _validate_request_shape(module):

    pool_uuid = module.params["pool_uuid"]
    subresource = module.params["subresource"]

    if subresource and not pool_uuid:
        module.fail_json(msg="subresource requires pool_uuid")

    if subresource and subresource not in POOL_SUBRESOURCES:
        module.fail_json(msg=f"Invalid subresource: {subresource}")

    provided = _provided_optional_params(module)
    allowed = allowed_request_parameters(POOL_SUBRESOURCES, pool_uuid, subresource)

    if not pool_uuid:
        allowed = STANDARD_COLLECTION_PARAMS
        label = "pool collection request"
    elif not subresource:
        allowed = set()
        label = "pool detail request"
    else:
        allowed = POOL_SUBRESOURCES[subresource]["supported_params"]
        label = f"pool subresource '{subresource}'"

    fail_on_unsupported_params(module, provided, allowed, label)


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            dict(
                pool_uuid=dict(type="str"),
                subresource=dict(type="str", choices=list(POOL_SUBRESOURCES.keys())),
                fields=dict(type="list", elements="str"),
                filter=dict(type="list", elements="str"),
                limit=dict(type="int"),
                ndjson=dict(type="bool"),
                markdown=dict(type="bool"),
                granularity=dict(type="str"),
            ),
        ),
        supports_check_mode=True,
    )

    validate_auth(module)
    _validate_request_shape(module)

    path = build_resource_path(module.params.get("pool_uuid"), module.params.get("subresource"))
    params = build_query_params(module)

    try:
        client = new_xoa_client(module)
        response, status_code = client.get("pools", path, params=params)

    except Exception as e:
        module.fail_json(msg=str(e))

    if status_code != 200:
        module.fail_json(msg=f"Unexpected status code: {status_code}")

    module.exit_json(changed=False, result=response)


if __name__ == "__main__":
    main()
