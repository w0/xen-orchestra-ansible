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


def _present(module, client):
    path = f"{module.params['vm_uuid']}/actions/snapshot"
    body = dict(name_label=module.params["snapshot_name"])
    params = dict(sync=module.params["sync"])

    response, status_code = client.post(
        "vms",
        path=path,
        body=body,
        params=params,
    )

    if status_code not in (201, 202):
        module.fail_json(
            msg="VM Snapshot creation failed", result=response, status_code=status_code
        )

    module.exit_json(
        changed=True,
        msg="VM Snapshot created successfully",
        result=response,
        status_code=status_code,
    )


def _absent(module, client):
    path = module.params["snapshot_uuid"]

    response, status_code = client.delete("vm-snapshots", path=path)

    if status_code != 204:
        module.fail_json(
            msg="VM Snapshot deletion failed", result=response, status_code=status_code
        )

    module.exit_json(
        changed=True, msg="VM Snapshot deleted successfully", status_code=status_code
    )


def _rollback(module, client):
    """Rollback a VM snapshot. Placeholder implementation."""
    module.warn("rollback is not implemented")
    module.exit_json(changed=False)


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
            state=dict(
                type="str", choices=["present", "absent", "rollback"], default="present"
            ),
            snapshot_name=dict(type="str"),
            snapshot_uuid=dict(type="str"),
            sync=dict(type="bool", default=False),
        ),
        required_if=[
            ("state", "present", ["vm_uuid"]),
            ("state", "absent", ["snapshot_uuid"]),
            ("state", "rollback", ["snapshot_uuid"]),
        ],
        required_one_of=[["username", "token"]],
        required_together=[["username", "password"]],
        supports_check_mode=True,
    )

    state = module.params["state"]

    state_handler = {
        "present": _present,
        "absent": _absent,
        "rollback": _rollback,
    }

    try:
        client = _client(module)
        state_handler[state](module, client)

    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
