#!/usr/bin/python

DOCUMENTATION = r"""
---
module: xoa_vm_info
short_description: Gather information about Xen Orchestra virtual machines
description:
  - Gather information about virtual machines through the Xen Orchestra REST API.
  - When O(vm_uuid) is omitted, the module queries the VM collection endpoint and can
    filter, limit, and select fields from the returned VM list.
  - When O(vm_uuid) is provided without O(subresource), the module returns detailed
    information for the VM identified by O(vm_uuid).
  - When both O(vm_uuid) and O(subresource) are provided, the module returns the
    requested subresource for that VM.
  - Only one subresource can be queried per task.
version_added: "1.0.0"
author:
  - w0
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
      - UUID of the virtual machine to query.
      - When omitted, the module queries the VM collection endpoint.
      - Required when O(subresource) is specified.
    type: str
  subresource:
    description:
      - VM subresource to query for the VM identified by O(vm_uuid).
      - The module validates subresource-specific query parameters before making the API call.
      - O(alarms), O(backup-jobs), O(messages), O(tasks), and O(vdis) support
        O(fields), O(filter), O(limit), O(ndjson), and O(markdown).
      - O(dashboard) supports O(ndjson).
      - O(stats) supports O(granularity).
    type: str
    choices:
      - alarms
      - backup-jobs
      - dashboard
      - messages
      - stats
      - tasks
      - vdis
  fields:
    description:
      - List of fields to request from the Xen Orchestra API.
      - Values are joined with commas before being sent to Xen Orchestra.
      - Supported for VM collection queries and for the O(alarms), O(backup-jobs),
        O(messages), O(tasks), and O(vdis) subresources.
      - Ignored for VM detail queries, O(dashboard), and O(stats).
    type: list
    elements: str
  filter:
    description:
      - List of filter expressions to apply to the API request.
      - Values are joined with spaces before being sent to Xen Orchestra.
      - Filter syntax is defined by the Xen Orchestra REST API.
      - Supported for VM collection queries and for the O(alarms), O(backup-jobs),
        O(messages), O(tasks), and O(vdis) subresources.
      - Ignored for VM detail queries, O(dashboard), and O(stats).
    type: list
    elements: str
  limit:
    description:
      - Maximum number of objects to return.
      - Supported for VM collection queries and for the O(alarms), O(backup-jobs),
        O(messages), O(tasks), and O(vdis) subresources.
      - Ignored for VM detail queries, O(dashboard), and O(stats).
    type: int
  ndjson:
    description:
      - Request newline-delimited JSON output from the API when supported.
      - Supported for VM collection queries and for the O(alarms), O(backup-jobs),
        O(messages), O(tasks), and O(vdis) subresources.
      - Also supported for the O(dashboard) subresource.
      - Ignored for VM detail queries and O(stats).
    type: bool
  markdown:
    description:
      - Request markdown output from the API when supported.
      - Supported for VM collection queries and for the O(alarms), O(backup-jobs),
        O(messages), O(tasks), and O(vdis) subresources.
      - Ignored for VM detail queries, O(dashboard), and O(stats).
    type: bool
  granularity:
    description:
      - Statistics granularity to request when querying the O(stats) subresource.
      - Valid values are C(seconds), C(minutes), C(hours), and C(days).
      - This value is passed directly to the Xen Orchestra API.
      - Only supported with O(subresource=stats).
    type: str
    choices:
      - seconds
      - minutes
      - hours
      - days
notes:
  - Authentication must be either C(token) alone or C(username) and C(password) together.
  - This module maps to the Xen Orchestra C(/vms), C(/vms/{id}), and selected
    C(/vms/{id}/{subresource}) endpoints.
  - The module validates unsupported parameter combinations before making the API call.
requirements:
  - python >= 3.9
"""

EXAMPLES = r"""
- name: List VMs with selected fields
  w0.xen_orchestra.xoa_vm_info:
    api_host: xo.example.com
    username: admin
    password: secret
    fields:
      - uuid
      - name_label
      - power_state
    filter:
      - power_state:running
    limit: 10

- name: Get a single VM by UUID
  w0.xen_orchestra.xoa_vm_info:
    api_host: xo.example.com
    username: admin
    password: secret
    vm_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c

- name: Get VM messages with selected fields
  w0.xen_orchestra.xoa_vm_info:
    api_host: xo.example.com
    username: admin
    password: secret
    vm_uuid: cef5f68c-61ae-3831-d2e6-1590d4934acf
    subresource: messages
    fields:
      - name
      - id
      - $object
    filter:
      - name:VM_STARTED
    limit: 5

- name: Get VM alarms
  w0.xen_orchestra.xoa_vm_info:
    api_host: xo.example.com
    username: admin
    password: secret
    vm_uuid: f07ab729-c0e8-721c-45ec-f11276377030
    subresource: alarms
    fields:
      - id
      - time

- name: Get VM tasks with token authentication
  w0.xen_orchestra.xoa_vm_info:
    api_host: xo.example.com
    token: "{{ xo_token }}"
    vm_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c
    subresource: tasks
    filter:
      - status:failure
    limit: 5

- name: Get VM stats
  w0.xen_orchestra.xoa_vm_info:
    api_host: xo.example.com
    username: admin
    password: secret
    vm_uuid: f07ab729-c0e8-721c-45ec-f11276377030
    subresource: stats
    granularity: seconds

- name: Get VM dashboard
  w0.xen_orchestra.xoa_vm_info:
    api_host: xo.example.com
    username: admin
    password: secret
    vm_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c
    subresource: dashboard
"""

RETURN = r"""
result:
  description:
    - Data returned by the Xen Orchestra API.
    - The return shape depends on the request mode.
    - VM collection queries return a list of VM records.
    - VM detail queries return a single VM object.
    - Subresource queries return the corresponding subresource payload.
  returned: success
  type: raw
changed:
  description:
    - Always C(false) for this info module.
  returned: always
  type: bool
  sample: false
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.w0.xen_orchestra.plugins.module_utils.xoa import (  # type: ignore
    build_xoa_argument_spec,
    new_xoa_client,
    validate_auth,
)
from ansible_collections.w0.xen_orchestra.plugins.module_utils.xoa_info import (  # type: ignore
    STANDARD_COLLECTION_PARAMS,
    allowed_request_parameters,
    build_resource_path,
)

VM_SUBRESOURCES = {
    "alarms": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "backup-jobs": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "dashboard": {"supported_params": {"ndjson"}},
    "messages": {"supported_params": STANDARD_COLLECTION_PARAMS},
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


def _validate_request_shape(module, allowed):
    """
    Validates the request shape and raises an error if it is invalid.
    """

    vm_uuid = module.params["vm_uuid"]
    subresource = module.params["subresource"]

    if subresource and not vm_uuid:
        module.fail_json(msg="subresource requires vm_uuid")

    if subresource and subresource not in VM_SUBRESOURCES:
        module.fail_json(msg=f"Invalid subresource: {subresource}")

    provided = _provided_optional_params(module)

    unsupported = sorted(provided - allowed)
    if unsupported:
        if vm_uuid and subresource:
            module.fail_json(
                msg=f"Unsupported parameters for vm subresource '{subresource}': {', '.join(unsupported)}"
            )
        elif vm_uuid:
            module.fail_json(
                msg=f"Unsupported parameters for vm detail request: {', '.join(unsupported)}"
            )
        else:
            module.fail_json(
                msg=f"Unsupported parameters for vm collection request: {', '.join(unsupported)}"
            )


def _build_query_params(module, allowed_params):
    params = {}

    if "fields" in allowed_params and module.params["fields"]:
        params["fields"] = ",".join(module.params["fields"])

    if "filter" in allowed_params and module.params["filter"]:
        params["filter"] = " ".join(module.params["filter"])

    if "limit" in allowed_params and module.params["limit"] is not None:
        params["limit"] = module.params["limit"]

    if "ndjson" in allowed_params and module.params["ndjson"] is not None:
        params["ndjson"] = module.params["ndjson"]

    if "markdown" in allowed_params and module.params["markdown"] is not None:
        params["markdown"] = module.params["markdown"]

    if "granularity" in allowed_params and module.params["granularity"]:
        params["granularity"] = module.params["granularity"]

    return params or None


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            dict(
                vm_uuid=dict(type="str"),
                subresource=dict(type="str", choices=sorted(VM_SUBRESOURCES.keys())),
                fields=dict(type="list", elements="str"),
                filter=dict(type="list", elements="str"),
                limit=dict(type="int"),
                ndjson=dict(type="bool"),
                markdown=dict(type="bool"),
                granularity=dict(type="str"),
            )
        ),
    )

    object_id = module.params.get("vm_uuid")
    subresource = module.params.get("subresource")

    validate_auth(module)
    allowed_params = allowed_request_parameters(VM_SUBRESOURCES, object_id, subresource)

    _validate_request_shape(module, allowed_params)

    path = build_resource_path(object_id, subresource)
    params = _build_query_params(module, allowed_params)

    try:
        client = new_xoa_client(module)
        response, status_code = client.get("vms", path, params=params)

    except Exception as e:
        module.fail_json(msg=str(e))

    if status_code != 200:
        module.fail_json(msg=f"Unexpected status code: {status_code}")

    module.exit_json(changed=False, result=response)


if __name__ == "__main__":
    main()
