from posix import stat

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
    pass


def _absent(module, client):
    pass


def _rollback(module, client):
    pass


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_host=dict(type="str", required=True),
            username=dict(type="str", required=True),
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
            snapshot_description=dict(type="str"),
        ),
        required_if=[
            ("state", "absent", ["snapshot_uuid"]),
            ("state", "rollback", ["snapshot_uuid"]),
        ],
        required_one_of=[["username", "token"]],
        required_together=[["username", "password"]],
        supports_check_mode=False,
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
