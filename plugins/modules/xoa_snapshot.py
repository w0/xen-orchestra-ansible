#!/usr/bin/python

DOCUMENTATION = r"""
---
module: xoa_snapshot
short_description: Manage Xen Orchestra VM snapshots
description:
  - Create and delete Xen Orchestra VM snapshots.
  - Rollback is accepted as a state, but it is not implemented.
version_added: "1.0.0"
options:
  api_host:
    description:
      - Xen Orchestra API host.
    required: true
    type: str
  username:
    description:
      - Username for Xen Orchestra authentication.
      - Use with C(password) when authenticating with username and password.
      - Must not be used with C(token).
    type: str
  password:
    description:
      - Password for Xen Orchestra authentication.
      - Use with C(username) when authenticating with username and password.
      - Must not be used with C(token).
    type: str
    no_log: true
  token:
    description:
      - API token for Xen Orchestra authentication.
      - Use by itself when authenticating with a token.
      - Must not be used with C(username) or C(password).
    type: str
    no_log: true
  use_ssl:
    description:
      - Whether to connect to Xen Orchestra over HTTPS.
    type: bool
    default: true
  validate_certs:
    description:
      - Whether to validate TLS certificates.
    type: bool
    default: true
  vm_uuid:
    description:
      - UUID of the VM to snapshot.
      - Required when C(state=present).
    type: str
  state:
    description:
      - Desired state of the snapshot.
      - C(present) creates a snapshot.
      - C(absent) deletes a snapshot.
      - C(rollback) is accepted but not implemented.
    type: str
    choices:
      - present
      - absent
      - rollback
    default: present
  snapshot_name:
    description:
      - Optional name to assign to the created snapshot.
      - If omitted, Xen Orchestra uses the VM name.
      - Used when C(state=present).
    type: str
  snapshot_uuid:
    description:
      - UUID of the snapshot to delete.
      - Required when C(state=absent) or C(state=rollback).
    type: str
  sync:
    description:
      - Whether snapshot creation should be synchronous.
    type: bool
    default: false
author:
  - Your Name Here
notes:
  - Authentication must be either C(token) alone or C(username) and C(password) together.
  - C(rollback) is accepted as a state but only emits a warning and returns C(changed=false).
  - The module supports check mode, but it does not currently change behavior when check mode is enabled.
"""

EXAMPLES = r"""
- name: Create a VM snapshot
  w0.xen_orchestra.xoa_snapshot:
    api_host: xo.example.com
    username: admin
    password: secret
    vm_uuid: 00000000-0000-0000-0000-000000000000
    snapshot_name: pre-upgrade
    state: present
    sync: false

- name: Delete a snapshot
  w0.xen_orchestra.xoa_snapshot:
    api_host: xo.example.com
    token: "{{ xo_api_token }}"
    snapshot_uuid: 11111111-1111-1111-1111-111111111111
    state: absent

- name: Attempt rollback to a snapshot
  w0.xen_orchestra.xoa_snapshot:
    api_host: xo.example.com
    username: admin
    password: secret
    snapshot_uuid: 11111111-1111-1111-1111-111111111111
    state: rollback
"""

RETURN = r"""
changed:
  description:
    - Whether any change was made.
  returned: always
  type: bool
msg:
  description:
    - Human-readable result message.
  returned: when available
  type: str
status_code:
  description:
    - HTTP status code returned by the Xen Orchestra API.
  returned: when available
  type: int
result:
  description:
    - Raw response payload from the Xen Orchestra API.
  returned: when available
  type: raw
"""

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
        supports_check_mode=True,
    )

    if module.params["token"]:
        if module.params["username"] or module.params["password"]:
            module.fail_json(msg="Token cannot be used with username or password")
    elif module.params["username"] and module.params["password"]:
        pass
    else:
        module.fail_json(msg="Either token or username/password must be provided")

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
