DOCUMENTATION = r"""
---
module: xoa_pif_info
short_description: Gather information about Xen Orchestra physical interfaces
description:
  - Gather information about physical interfaces through the Xen Orchestra REST API.
  - When O(pif_uuid) is omitted, the module queries the physical interface collection endpoint
    and can filter, limit, and select fields from the returned physical interface list.
  - When O(pif_uuid) is provided without O(subresource), the module returns detailed
    information for the physical interface identified by O(pif_uuid).
  - When both O(pif_uuid) and O(subresource) are provided, the module returns the
    requested subresource for that physical interface.
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
  pif_uuid:
    description:
      - UUID of the physical interface to query.
      - When omitted, the module queries the physical interface collection endpoint.
      - Required when O(subresource) is specified.
    type: str
  subresource:
    description:
      - Physical interface subresource to query for the physical interface identified by
        O(pif_uuid).
      - The module validates subresource-specific query parameters before making the API call.
      - O(alarms), O(messages), and O(tasks) support O(fields), O(filter), O(limit),
        O(ndjson), and O(markdown).
    type: str
    choices:
      - alarms
      - messages
      - tasks
  fields:
    description:
      - List of fields to request from the Xen Orchestra API.
      - Values are joined with commas before being sent to Xen Orchestra.
      - Supported for physical interface collection queries and for the O(alarms),
        O(messages), and O(tasks) subresources.
      - Ignored for physical interface detail queries.
    type: list
    elements: str
  filter:
    description:
      - List of filter expressions to apply to the API request.
      - Values are joined with spaces before being sent to Xen Orchestra.
      - Filter syntax is defined by the Xen Orchestra REST API.
      - Supported for physical interface collection queries and for the O(alarms),
        O(messages), and O(tasks) subresources.
      - Ignored for physical interface detail queries.
    type: list
    elements: str
  limit:
    description:
      - Maximum number of objects to return.
      - Supported for physical interface collection queries and for the O(alarms),
        O(messages), and O(tasks) subresources.
      - Ignored for physical interface detail queries.
    type: int
  ndjson:
    description:
      - Request newline-delimited JSON output from the API when supported.
      - Supported for physical interface collection queries and for the O(alarms),
        O(messages), and O(tasks) subresources.
      - Ignored for physical interface detail queries.
    type: bool
  markdown:
    description:
      - Request markdown output from the API when supported.
      - Supported for physical interface collection queries and for the O(alarms),
        O(messages), and O(tasks) subresources.
      - Ignored for physical interface detail queries.
    type: bool
notes:
  - Authentication must be either C(token) alone or C(username) and C(password) together.
  - This module maps to the Xen Orchestra C(/pifs), C(/pifs/{id}), and selected
    C(/pifs/{id}/{subresource}) endpoints.
  - The module validates unsupported parameter combinations before making the API call.
requirements:
  - python >= 3.9
"""

EXAMPLES = r"""
- name: List physical interfaces with selected fields
  w0.xen_orchestra.xoa_pif_info:
    api_host: xo.example.com
    username: admin
    password: secret
    fields:
      - uuid
      - device
      - ip
    limit: 10

- name: Get a single physical interface by UUID
  w0.xen_orchestra.xoa_pif_info:
    api_host: xo.example.com
    username: admin
    password: secret
    pif_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c

- name: Get physical interface messages with selected fields
  w0.xen_orchestra.xoa_pif_info:
    api_host: xo.example.com
    username: admin
    password: secret
    pif_uuid: cef5f68c-61ae-3831-d2e6-1590d4934acf
    subresource: messages
    fields:
      - name
      - id
      - $object
    filter:
      - name:PIF_PLUGGED
    limit: 5

- name: Get physical interface alarms
  w0.xen_orchestra.xoa_pif_info:
    api_host: xo.example.com
    username: admin
    password: secret
    pif_uuid: f07ab729-c0e8-721c-45ec-f11276377030
    subresource: alarms
    fields:
      - id
      - time

- name: Get physical interface tasks with token authentication
  w0.xen_orchestra.xoa_pif_info:
    api_host: xo.example.com
    token: "{{ xo_token }}"
    pif_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c
    subresource: tasks
    filter:
      - status:failure
    limit: 5
"""

RETURN = r"""
result:
  description:
    - Data returned by the Xen Orchestra API.
    - The return shape depends on the request mode.
    - Physical interface collection queries return a list of physical interface records.
    - Physical interface detail queries return a single physical interface object.
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
    build_query_params,
    build_resource_path,
    fail_on_unsupported_params,
    provided_optional_params,
)

PIF_SUBRESOURCES = {
    "alarms": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "messages": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "tasks": {"supported_params": STANDARD_COLLECTION_PARAMS},
}


def _validate_request_shape(module):

    pif_uuid = module.params["pif_uuid"]
    subresource = module.params["subresource"]

    if subresource and not pif_uuid:
        module.fail_json(msg="subresource requires pif_uuid")

    if subresource and subresource not in PIF_SUBRESOURCES:
        module.fail_json(msg=f"Invalid subresource: {subresource}")

    provided = provided_optional_params(module)
    allowed = allowed_request_parameters(PIF_SUBRESOURCES, pif_uuid, subresource)

    if not pif_uuid:
        allowed = STANDARD_COLLECTION_PARAMS
        label = "pif collection request"
    elif not subresource:
        allowed = set()
        label = "pif detail request"
    else:
        allowed = PIF_SUBRESOURCES[subresource]["supported_params"]
        label = f"pif subresource '{subresource}'"

    fail_on_unsupported_params(module, provided, allowed, label)


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            pif_uuid=dict(type="str"),
            subresource=dict(type="str", choices=list(PIF_SUBRESOURCES.keys())),
            fields=dict(type="list", elements="str"),
            filter=dict(type="list", elements="str"),
            limit=dict(type="int"),
            ndjson=dict(type="bool"),
            markdown=dict(type="bool"),
        )
    )

    validate_auth(module)
    _validate_request_shape(module)

    path = build_resource_path(module.params["pif_uuid"], module.params["subresource"])
    params = build_query_params(module)

    try:
        client = new_xoa_client(module)
        response, status_code = client.get("pifs", path, params=params)

    except Exception as e:
        module.fail_json(msg=str(e))

    if status_code != 200:
        module.fail_json(msg=f"Unexpected status code: {status_code}")

    module.exit_json(changed=False, result=response)


if __name__ == "__main__":
    main()
