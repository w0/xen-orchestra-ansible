#!/usr/bin/python

DOCUMENTATION = r"""
---
module: xoa_snapshot_info
short_description: Gather information about Xen Orchestra VM snapshots
description:
  - Gather information about VM snapshots through the Xen Orchestra REST API.
  - Query snapshots by snapshot UUID, snapshot name, VM UUID, or additional filter and field combinations.
  - When filtering by snapshot name or VM UUID, the module automatically adds the minimum fields needed for filtering and returned data.
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
      - Filter snapshots belonging to the VM identified by this UUID.
      - Ignored when C(snapshot_uuid) is set.
    type: str
  snapshot_name:
    description:
      - Filter snapshots by exact snapshot name.
      - Matching is exact and case-sensitive.
      - Ignored when C(snapshot_uuid) is set.
    type: str
  snapshot_uuid:
    description:
      - Fetch a single snapshot by UUID.
      - When set, C(snapshot_name), C(vm_uuid), C(filter), C(limit), and C(fields) are ignored.
    type: str
  fields:
    description:
      - List of fields to request from Xen Orchestra.
      - Defaults to C(uuid), C(snapshot_time), and C($snapshot_of).
      - C(name_label) is automatically added when C(snapshot_name) is set.
      - C($snapshot_of) is automatically added when C(vm_uuid) is set.
      - Ignored when C(snapshot_uuid) is set.
    type: list
    elements: str
    default:
      - uuid
      - snapshot_time
      - $snapshot_of
  filter:
    description:
      - Additional Xen Orchestra filter expressions.
      - Expressions are joined with spaces and sent directly to Xen Orchestra.
      - Ignored when C(snapshot_uuid) is set.
    type: list
    elements: str
  limit:
    description:
      - Maximum number of snapshots to return.
      - Ignored when C(snapshot_uuid) is set.
    type: int
author:
  - w0
notes:
  - Authentication must be either C(token) alone or C(username) and C(password) together.
  - This module maps to the Xen Orchestra C(/vm-snapshots) and C(/vm-snapshots/{id}) endpoints.
  - The module always calls Xen Orchestra's C(vm-snapshots) endpoint.
  - If C(snapshot_uuid) is provided, the module performs a direct lookup using that UUID as the path segment.
  - If C(snapshot_uuid) is provided, the module warns when other query options are also set.
  - C(snapshot_name) is converted to an exact regular expression filter using C(re.escape()).
  - C(vm_uuid) is converted into a filter of the form C($snapshot_of:"<uuid>").
  - The module always returns the response under C(snapshots); a single object response is normalized into a one-element list.
"""

EXAMPLES = r"""
- name: Get all snapshots using the default fields
  w0.xen_orchestra.xoa_snapshot_info:
    api_host: xo.example.com
    username: admin
    password: secret

- name: Get a snapshot by UUID
  w0.xen_orchestra.xoa_snapshot_info:
    api_host: xo.example.com
    token: "{{ xo_token }}"
    snapshot_uuid: 0d1c2b3a-4567-89ab-cdef-0123456789ab

- name: Get snapshots for a VM
  w0.xen_orchestra.xoa_snapshot_info:
    api_host: xo.example.com
    username: admin
    password: secret
    vm_uuid: 7b1f3d20-1234-4567-89ab-0123456789ab

- name: Get snapshots by exact name
  w0.xen_orchestra.xoa_snapshot_info:
    api_host: xo.example.com
    token: "{{ xo_token }}"
    snapshot_name: daily-backup

- name: Get snapshots with additional filters and custom fields
  w0.xen_orchestra.xoa_snapshot_info:
    api_host: xo.example.com
    username: admin
    password: secret
    vm_uuid: 7b1f3d20-1234-4567-89ab-0123456789ab
    filter:
      - snapshot_time:>="2024-01-01T00:00:00Z"
    fields:
      - uuid
      - snapshot_time
      - name_label

- name: Get the most recent snapshots for a VM
  w0.xen_orchestra.xoa_snapshot_info:
    api_host: xo.example.com
    token: "{{ xo_token }}"
    vm_uuid: 7b1f3d20-1234-4567-89ab-0123456789ab
    limit: 5
"""

RETURN = r"""
snapshots:
  description:
    - List of snapshot records returned by Xen Orchestra.
    - When C(snapshot_uuid) is used, a single object response is normalized into a one-item list.
  returned: always
  type: list
  elements: dict
  sample:
    - uuid: 0d1c2b3a-4567-89ab-cdef-0123456789ab
      snapshot_time: "2024-01-01T12:34:56Z"
      $snapshot_of: 7b1f3d20-1234-4567-89ab-0123456789ab
"""


import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.w0.xen_orchestra.plugins.module_utils.xoa import (  # type: ignore
    build_xoa_argument_spec,
    new_xoa_client,
    validate_auth,
)

SNAPSHOT_DEFAULT_FIELDS = ["uuid", "snapshot_time", "$snapshot_of"]


def main():

    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            dict(
                vm_uuid=dict(type="str"),
                snapshot_name=dict(type="str"),
                snapshot_uuid=dict(type="str"),
                fields=dict(type="list", default=SNAPSHOT_DEFAULT_FIELDS),
                filter=dict(type="list"),
                limit=dict(type="int"),
            )
        ),
        mutually_exclusive=[["snapshot_name", "snapshot_uuid"]],
        supports_check_mode=True,
    )

    validate_auth(module)

    if module.params["snapshot_uuid"]:
        ignored = {
            "snapshot_name": module.params.get("snapshot_name"),
            "vm_uuid": module.params.get("vm_uuid"),
            "filter": module.params.get("filter"),
            "limit": module.params.get("limit"),
            "fields": module.params.get("fields"),
        }

        for name, value in ignored.items():
            if value not in (None, [], "", SNAPSHOT_DEFAULT_FIELDS):
                module.warn(f"{name} is ignored when snapshot_uuid is provided")

        path = module.params["snapshot_uuid"]
        params = None

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

    try:
        client = new_xoa_client(module)
        response, status_code = client.get("vm-snapshots", path, params)
    except Exception as e:
        module.fail_json(msg=str(e))

    if status_code != 200:
        module.fail_json(
            msg="Failed to get snapshot info", result=response, status_code=status_code
        )

    if isinstance(response, dict):
        response = [response]

    module.exit_json(changed=False, snapshots=response)


if __name__ == "__main__":
    main()
