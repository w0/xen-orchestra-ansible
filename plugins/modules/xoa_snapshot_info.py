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


def _filter_by_vm_uuid(response, vm_uuid):
    filtered = []
    for snapshot in response:
        if snapshot.get("$snapshot_of") == vm_uuid:
            filtered.append(snapshot)

    return filtered


def _filter_by_name_label(response, snapshot_name):
    filtered = []
    for snapshot in response:
        if snapshot.get("name_label") == snapshot_name:
            filtered.append(snapshot)

    return filtered


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
            limit=dict(type="int"),
        ),
        mutually_exclusive=["snapshot_name", "snapshot_uuid"],
        required_one_of=[["username", "token"]],
        required_together=[["username", "password"]],
        supports_check_mode=True,
    )

    client = _client(module)

    if module.params["snapshot_uuid"]:
        path = module.params["snapshot_uuid"]
        params = None
        if module.params["fields"] != ["uuid", "snapshot_time", "$snapshot_of"]:
            module.warn("fields parameter is ignored when snapshot_uuid is provided")
        if module.params["limit"]:
            module.warn("limit parameter is ignored when snapshot_uuid is provided")
    elif module.params["snapshot_name"]:
        path = None
        fields = list(module.params["fields"])
        if "name_label" not in fields:
            fields.append("name_label")

        params = dict(
            fields=",".join(fields),
            limit=module.params["limit"],
        )
    else:
        path = None
        params = dict(
            fields=",".join(module.params["fields"]),
            limit=module.params["limit"],
        )

    response, status_code = client.get("vm-snapshots", path, params)

    if status_code != 200:
        module.fail_json(
            msg="Failed to get snapshot info", result=response, status_code=status_code
        )

    if module.params["snapshot_uuid"]:
        module.exit_json(changed=False, snapshots=[response])

    if vm_uuid := module.params["vm_uuid"]:
        response = _filter_by_vm_uuid(response, vm_uuid)

    if snapshot_name := module.params["snapshot_name"]:
        response = _filter_by_name_label(response, snapshot_name)

    module.exit_json(changed=False, snapshots=response)


if __name__ == "__main__":
    main()
