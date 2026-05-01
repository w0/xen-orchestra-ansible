#!/usr/bin/python

DOCUMENTATION = r"""
---
module: xoa_network_info
short_description: Gather information about Xen Orchestra networks
description:
  - Gather information about networks through the Xen Orchestra REST API.
  - When O(network_uuid) is omitted, the module queries the network collection endpoint and can
    filter, limit, and select fields from the returned network list.
  - When O(network_uuid) is provided without O(subresource), the module returns detailed
    information for the network identified by O(network_uuid).
  - When both O(network_uuid) and O(subresource) are provided, the module returns the
    requested subresource for that network.
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
  network_uuid:
    description:
      - UUID of the network to query.
      - When omitted, the module queries the network collection endpoint.
      - Required when O(subresource) is specified.
    type: str
  subresource:
    description:
      - Network subresource to query for the network identified by O(network_uuid).
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
      - Supported for network collection queries and for the O(alarms), O(messages), and
        O(tasks) subresources.
      - Ignored for network detail queries.
    type: list
    elements: str
  filter:
    description:
      - List of filter expressions to apply to the API request.
      - Values are joined with spaces before being sent to Xen Orchestra.
      - Filter syntax is defined by the Xen Orchestra REST API.
      - Supported for network collection queries and for the O(alarms), O(messages), and
        O(tasks) subresources.
      - Ignored for network detail queries.
    type: list
    elements: str
  limit:
    description:
      - Maximum number of objects to return.
      - Supported for network collection queries and for the O(alarms), O(messages), and
        O(tasks) subresources.
      - Ignored for network detail queries.
    type: int
  ndjson:
    description:
      - Request newline-delimited JSON output from the API when supported.
      - Supported for network collection queries and for the O(alarms), O(messages), and
        O(tasks) subresources.
      - Ignored for network detail queries.
    type: bool
  markdown:
    description:
      - Request markdown output from the API when supported.
      - Supported for network collection queries and for the O(alarms), O(messages), and
        O(tasks) subresources.
      - Ignored for network detail queries.
    type: bool
notes:
  - Authentication must be either C(token) alone or C(username) and C(password) together.
  - This module maps to the Xen Orchestra C(/networks), C(/networks/{id}), and selected
    C(/networks/{id}/{subresource}) endpoints.
  - The module validates unsupported parameter combinations before making the API call.
requirements:
  - python >= 3.9
"""

EXAMPLES = r"""
- name: List networks with selected fields
  w0.xen_orchestra.xoa_network_info:
    api_host: xo.example.com
    username: admin
    password: secret
    fields:
      - uuid
      - name_label
      - defaultIsLocked
    limit: 10

- name: Get a single network by UUID
  w0.xen_orchestra.xoa_network_info:
    api_host: xo.example.com
    username: admin
    password: secret
    network_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c

- name: Get network messages with selected fields
  w0.xen_orchestra.xoa_network_info:
    api_host: xo.example.com
    username: admin
    password: secret
    network_uuid: cef5f68c-61ae-3831-d2e6-1590d4934acf
    subresource: messages
    fields:
      - name
      - id
      - $object
    filter:
      - name:NETWORK_CREATED
    limit: 5

- name: Get network alarms
  w0.xen_orchestra.xoa_network_info:
    api_host: xo.example.com
    username: admin
    password: secret
    network_uuid: f07ab729-c0e8-721c-45ec-f11276377030
    subresource: alarms
    fields:
      - id
      - time

- name: Get network tasks with token authentication
  w0.xen_orchestra.xoa_network_info:
    api_host: xo.example.com
    token: "{{ xo_token }}"
    network_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c
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
    - Network collection queries return a list of network records.
    - Network detail queries return a single network object.
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

VIF_SUBRESOURCES = {
    "alarms": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "messages": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "tasks": {"supported_params": STANDARD_COLLECTION_PARAMS},
}


def _validate_request_shape(module):

    network_uuid = module.params["network_uuid"]
    subresource = module.params["subresource"]

    if subresource and not network_uuid:
        module.fail_json(msg="subresource requires network_uuid")

    if subresource and subresource not in VIF_SUBRESOURCES:
        module.fail_json(msg=f"Invalid subresource: {subresource}")

    provided = provided_optional_params(module)
    allowed = allowed_request_parameters(VIF_SUBRESOURCES, network_uuid, subresource)

    if not network_uuid:
        allowed = STANDARD_COLLECTION_PARAMS
        label = "network collection request"
    elif not subresource:
        allowed = set()
        label = "network detail request"
    else:
        allowed = VIF_SUBRESOURCES[subresource]["supported_params"]
        label = f"network subresource '{subresource}'"

    fail_on_unsupported_params(module, provided, allowed, label)


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            network_uuid=dict(type="str"),
            subresource=dict(type="str", choices=list(VIF_SUBRESOURCES.keys())),
            fields=dict(type="list", elements="str"),
            filter=dict(type="list", elements="str"),
            limit=dict(type="int"),
            ndjson=dict(type="bool"),
            markdown=dict(type="bool"),
        )
    )

    validate_auth(module)
    _validate_request_shape(module)

    path = build_resource_path(module.params["network_uuid"], module.params["subresource"])
    params = build_query_params(module)

    try:
        client = new_xoa_client(module)
        response, status_code = client.get("networks", path, params=params)

    except Exception as e:
        module.fail_json(msg=str(e))

    if status_code != 200:
        module.fail_json(msg=f"Unexpected status code: {status_code}")

    module.exit_json(changed=False, result=response)


if __name__ == "__main__":
    main()
