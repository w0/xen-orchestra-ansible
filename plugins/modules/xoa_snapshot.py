#!/usr/bin/python

DOCUMENTATION = r"""
---
module: xoa_snapshot
short_description: Manage Xen Orchestra VM snapshots
description:
  - Create and delete VM snapshots through the Xen Orchestra REST API.
  - Use O(state=present) to create a snapshot for a VM.
  - Use O(state=absent) to delete an existing snapshot by UUID.
  - O(state=rollback) is accepted for interface compatibility, but rollback is not implemented by this module.
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
      - Desired state of the VM snapshot.
      - C(present) creates a snapshot for the VM identified by O(vm_uuid).
      - C(absent) deletes the snapshot identified by O(snapshot_uuid).
      - C(rollback) is accepted for interface compatibility, but it is not implemented.
    type: str
    choices:
      - present
      - absent
      - rollback
    default: present
  snapshot_name:
    description:
      - Optional name to assign to the snapshot being created.
      - If omitted, Xen Orchestra uses its default snapshot naming behavior.
      - Only used when C(state=present).
    type: str
  snapshot_uuid:
    description:
      - UUID of the snapshot to act on.
      - Required when C(state=absent) or C(state=rollback).
      - Ignored when C(state=present).
    type: str
  sync:
    description:
      - Whether the snapshot creation request should be performed synchronously.
      - Only used when C(state=present).
    type: bool
    default: false
author:
  - w0
notes:
  - Authentication must be either C(token) alone or C(username) and C(password) together.
  - This module maps to the Xen Orchestra C(/vms/{id}/actions/snapshot) and C(/vm-snapshots/{id}) endpoints.
  - C(rollback) is accepted as a state but only emits a warning and returns C(changed=false).
  - This module does not support check mode.
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

- name: Create a VM snapshot using token authentication
  w0.xen_orchestra.xoa_snapshot:
    api_host: xo.example.com
    token: "{{ xo_api_token }}"
    vm_uuid: 00000000-0000-0000-0000-000000000000
    state: present

- name: Delete a snapshot by UUID
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
    - Whether the module reports a change.
    - Snapshot creation and deletion report C(true) on success.
    - Rollback always reports C(false) because it is not implemented.
  returned: always
  type: bool
msg:
  description:
    - Human-readable result message.
  returned: always
  type: str
status_code:
  description:
    - HTTP status code returned by the Xen Orchestra API.
  returned: when available
  type: int
result:
  description:
    - Raw response payload returned by the Xen Orchestra API.
    - Present when Xen Orchestra returns a response body for the operation.
  returned: when available
  type: raw
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.w0.xen_orchestra.plugins.module_utils.xoa import (  # type: ignore
    build_xoa_argument_spec,
    new_xoa_client,
    validate_auth,
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

    module.exit_json(changed=True, msg="VM Snapshot deleted successfully", status_code=status_code)


def _rollback(module, client):
    """Rollback a VM snapshot. Placeholder implementation."""
    module.warn("rollback is not implemented")
    module.exit_json(changed=False)


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            dict(
                vm_uuid=dict(type="str"),
                state=dict(
                    type="str",
                    choices=["present", "absent", "rollback"],
                    default="present",
                ),
                snapshot_name=dict(type="str"),
                snapshot_uuid=dict(type="str"),
                sync=dict(type="bool", default=False),
            )
        ),
        required_if=[
            ("state", "present", ["vm_uuid"]),
            ("state", "absent", ["snapshot_uuid"]),
            ("state", "rollback", ["snapshot_uuid"]),
        ],
        supports_check_mode=False,
    )

    validate_auth(module)

    state = module.params["state"]

    state_handler = {
        "present": _present,
        "absent": _absent,
        "rollback": _rollback,
    }

    try:
        client = new_xoa_client(module)
        state_handler[state](module, client)

    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
