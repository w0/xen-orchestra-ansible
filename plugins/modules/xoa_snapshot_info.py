import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.w0.xen_orchestra.plugins.module_utils.xoa_client import (  # type: ignore
    XOAClient,
)


def _client(module):
    return XOAClient(
        api_host=module.params["api_host"],
        username=module.params["username"],
        password=module.params["password"],
        token=module.params["token"],
        use_ssl=module.params["use_ssl"],
        validate_certs=module.params["validate_certs"],
    )


def main():

    module = AnsibleModule(
        argument_spec=dict(
            api_host=dict(type="str", required=True),
            username=dict(type="str"),
            password=dict(type="str", no_log=True),
            token=dict(type="str", no_log=True),
            use_ssl=dict(type="bool", default=True),
            validate_certs=dict(type="bool", default=True),
            vm_uuid=dict(type="str"),
            snapshot_name=dict(type="str"),
            snapshot_uuid=dict(type="str"),
            fields=dict(type="list", default=["uuid", "snapshot_time", "$snapshot_of"]),
            filter=dict(type="list"),
            limit=dict(type="int"),
        ),
        mutually_exclusive=[["snapshot_name", "snapshot_uuid"]],
        required_one_of=[["username", "token"]],
        required_together=[["username", "password"]],
        supports_check_mode=True,
    )

    client = _client(module)

    if module.params["snapshot_uuid"]:
        ignored = ["snapshot_name", "vm_uuid", "filter", "fields", "limit"]

        for p in ignored:
            if module.params.get(p):
                module.warn(f"{p} is ignored when snapshot_uuid is set")

        path = module.params["snapshot_uuid"]
        params = None
        if module.params["fields"] != ["uuid", "snapshot_time", "$snapshot_of"]:
            module.warn("fields parameter is ignored when snapshot_uuid is provided")
        if module.params["limit"]:
            module.warn("limit parameter is ignored when snapshot_uuid is provided")
    else:
        path = None

        fields = list(module.params["fields"])
        filters = list(module.params["filter"] or [])

        if module.params["snapshot_name"]:
            name = re.escape(module.params["snapshot_name"])
            filters.append(f"name_label:/^{name}$/")
            if "name_label" not in fields:
                fields.append("name_label")

        if module.params["vm_uuid"]:
            uuid = module.params["vm_uuid"].replace('"', '\\"')
            filters.append(f'$snapshot_of:"{uuid}"')
            if "$snapshot_of" not in fields:
                fields.append("$snapshot_of")

        params = dict(
            fields=",".join(fields),
            filter=" ".join(filters),
            limit=module.params["limit"],
        )

    response, status_code = client.get("vm-snapshots", path, params)

    if status_code != 200:
        module.fail_json(
            msg="Failed to get snapshot info", result=response, status_code=status_code
        )

    if isinstance(response, dict):
        response = [response]

    module.exit_json(changed=False, snapshots=response)


if __name__ == "__main__":
    main()
