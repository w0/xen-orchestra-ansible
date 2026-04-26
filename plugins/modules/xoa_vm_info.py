#!/usr/bin/python

DOCUMENTATION = r"""
---
module: xoa_vm_info
short_description: Gather information about Xen Orchestra virtual machines
description:
  - Gather information about virtual machines from Xen Orchestra.
  - When O(vm_uuid) is omitted, the module queries the VM collection endpoint and can
    filter, limit, and select fields from the returned VM list.
  - When O(vm_uuid) is provided without O(subresource), the module returns detailed
    information for a single virtual machine.
  - When both O(vm_uuid) and O(subresource) are provided, the module returns a single
    VM subresource for that virtual machine.
  - Only one subresource can be queried per task.
version_added: "1.0.0"
author:
  - Kassidy
options:
  vm_uuid:
    description:
      - UUID of the virtual machine to query.
      - When omitted, the module queries the VM collection endpoint.
      - Required when O(subresource) is specified.
    type: str
  subresource:
    description:
      - VM subresource to query for the specified O(vm_uuid).
      - Subresource-specific query parameters are validated by the module.
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
      - List of fields to request from the API.
      - Values are joined with commas before being sent to Xen Orchestra.
      - Supported for VM collection queries and for the O(alarms), O(backup-jobs),
        O(messages), O(tasks), and O(vdis) subresources.
      - Not supported for VM detail queries, O(dashboard), or O(stats).
    type: list
    elements: str
  filter:
    description:
      - List of filter expressions to apply to the API request.
      - Values are joined with spaces before being sent to Xen Orchestra.
      - Filter syntax is defined by the Xen Orchestra REST API.
      - Supported for VM collection queries and for the O(alarms), O(backup-jobs),
        O(messages), O(tasks), and O(vdis) subresources.
      - Not supported for VM detail queries, O(dashboard), or O(stats).
    type: list
    elements: str
  limit:
    description:
      - Maximum number of objects to return.
      - Supported for VM collection queries and for the O(alarms), O(backup-jobs),
        O(messages), O(tasks), and O(vdis) subresources.
      - Not supported for VM detail queries, O(dashboard), or O(stats).
    type: int
  ndjson:
    description:
      - Request newline-delimited JSON output from the API when supported.
      - Supported for VM collection queries and for the O(alarms), O(backup-jobs),
        O(messages), O(tasks), and O(vdis) subresources.
      - Also supported for the O(dashboard) subresource.
      - Not supported for VM detail queries or O(stats).
    type: bool
  markdown:
    description:
      - Request markdown output from the API when supported.
      - Supported for VM collection queries and for the O(alarms), O(backup-jobs),
        O(messages), O(tasks), and O(vdis) subresources.
      - Not supported for VM detail queries, O(dashboard), or O(stats).
    type: bool
  granularity:
    description:
      - Statistics granularity to request when querying the O(stats) subresource.
      - This value is passed directly to the Xen Orchestra API.
      - Only supported with O(subresource=stats).
    type: str
extends_documentation_fragment:
  - w0.xen_orchestra.xoa
notes:
  - This module maps to the Xen Orchestra O(/vms), O(/vms/{id}), and selected
    O(/vms/{id}/{subresource}) REST API endpoints.
  - The module validates unsupported parameter combinations before making the API call.
requirements:
  - python >= 3.9
"""

EXAMPLES = r"""
- name: List VMs with selected fields
  w0.xen_orchestra.xoa_vm_info:
    url: https://xoa.example.invalid
    user: admin
    password: secret
    fields:
      - uuid
      - name_label
      - power_state
    filter:
      - power_state:running
    limit: 10

- name: Get a single VM
  w0.xen_orchestra.xoa_vm_info:
    url: https://xoa.example.invalid
    user: admin
    password: secret
    vm_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c

- name: Get VM messages
  w0.xen_orchestra.xoa_vm_info:
    url: https://xoa.example.invalid
    user: admin
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
    url: https://xoa.example.invalid
    user: admin
    password: secret
    vm_uuid: f07ab729-c0e8-721c-45ec-f11276377030
    subresource: alarms
    fields:
      - id
      - time

- name: Get VM stats
  w0.xen_orchestra.xoa_vm_info:
    url: https://xoa.example.invalid
    user: admin
    password: secret
    vm_uuid: f07ab729-c0e8-721c-45ec-f11276377030
    subresource: stats
    granularity: seconds

- name: Get VM dashboard
  w0.xen_orchestra.xoa_vm_info:
    url: https://xoa.example.invalid
    user: admin
    password: secret
    vm_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c
    subresource: dashboard
"""

RETURN = r"""
result:
  description:
    - Data returned by the Xen Orchestra API.
    - The return shape depends on the request mode.
    - VM collection queries return a list of VMs.
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

STANDARD_COLLECTION_PARAMS = {"fields", "filter", "limit", "ndjson", "markdown"}

VM_SUBRESOURCES = {
    "alarms": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "backup-jobs": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "dashboard": {"supported_params": {"ndjson"}},
    "messages": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "stats": {"supported_params": {"granularity"}},
    "tasks": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "vdis": {"supported_params": STANDARD_COLLECTION_PARAMS},
}


def _allowed_params_for_request(module):
    """
    Returns the allowed parameters for the current request shape.
    """

    vm_uuid = module.params["vm_uuid"]
    subresource = module.params["subresource"]

    if not vm_uuid:
        # No VM UUID provided, return standard collection params
        return STANDARD_COLLECTION_PARAMS

    if not subresource:
        # No subresource provided, return empty set
        return set()

    # Return the supported params for the given subresource
    return VM_SUBRESOURCES[subresource]["supported_params"]


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
    allowed = _allowed_params_for_request(module)

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


def _build_vm_path(module):
    """
    Builds the VM path for the current request shape.
    """
    vm_uuid = module.params["vm_uuid"]
    subresource = module.params["subresource"]

    if not vm_uuid:
        # No VM UUID provided, return None to indicate a collection request
        return None

    if not subresource:
        # No subresource provided, return the VM UUID to indicate a detail request
        return vm_uuid

    return f"{vm_uuid}/{subresource}"


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
                fields=dict(type="list", elements=str),
                filter=dict(type="list", elements=str),
                limit=dict(type="int"),
                ndjson=dict(type="bool"),
                markdown=dict(type="bool"),
                granularity=dict(type="str"),
            )
        ),
    )

    validate_auth(module)
    _validate_request_shape(module)

    path = _build_vm_path(module)
    allowed_params = _allowed_params_for_request(module)
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
