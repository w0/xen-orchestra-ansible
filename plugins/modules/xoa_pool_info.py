#!/usr/bin/python

DOCUMENTATION = r"""
---
module: xoa_pool_info
short_description: Gather information about Xen Orchestra pools
description:
  - Gather information about pools through the Xen Orchestra REST API.
  - When O(pool_uuid) is omitted, the module queries the pool collection endpoint and can
    filter, limit, and select fields from the returned pool list.
  - When O(pool_uuid) is provided without O(subresource), the module returns detailed
    information for the pool identified by O(pool_uuid).
  - When both O(pool_uuid) and O(subresource) are provided, the module returns the
    requested subresource for that pool.
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
  pool_uuid:
    description:
      - UUID of the pool to query.
      - When omitted, the module queries the pool collection endpoint.
      - Required when O(subresource) is specified.
    type: str
  subresource:
    description:
      - Pool subresource to query for the pool identified by O(pool_uuid).
      - The module validates subresource-specific query parameters before making the API call.
      - O(alarms), O(messages), and O(tasks) support O(fields), O(filter), O(limit),
        O(ndjson), and O(markdown).
      - O(dashboard) supports O(ndjson).
      - O(missing_patches) supports no additional query parameters.
      - O(stats) supports O(granularity).
    type: str
    choices:
      - alarms
      - dashboard
      - messages
      - missing_patches
      - stats
      - tasks
  fields:
    description:
      - List of fields to request from the Xen Orchestra API.
      - Values are joined with commas before being sent to Xen Orchestra.
      - Supported for pool collection queries and for the O(alarms), O(messages), and
        O(tasks) subresources.
      - Ignored for pool detail queries, O(dashboard), O(missing_patches), and O(stats).
    type: list
    elements: str
  filter:
    description:
      - List of filter expressions to apply to the API request.
      - Values are joined with spaces before being sent to Xen Orchestra.
      - Filter syntax is defined by the Xen Orchestra REST API.
      - Supported for pool collection queries and for the O(alarms), O(messages), and
        O(tasks) subresources.
      - Ignored for pool detail queries, O(dashboard), O(missing_patches), and O(stats).
    type: list
    elements: str
  limit:
    description:
      - Maximum number of objects to return.
      - Supported for pool collection queries and for the O(alarms), O(messages), and
        O(tasks) subresources.
      - Ignored for pool detail queries, O(dashboard), O(missing_patches), and O(stats).
    type: int
  ndjson:
    description:
      - Request newline-delimited JSON output from the API when supported.
      - Supported for pool collection queries and for the O(alarms), O(messages), and
        O(tasks) subresources.
      - Also supported for the O(dashboard) subresource.
      - Ignored for pool detail queries, O(missing_patches), and O(stats).
    type: bool
  markdown:
    description:
      - Request markdown output from the API when supported.
      - Supported for pool collection queries and for the O(alarms), O(messages), and
        O(tasks) subresources.
      - Ignored for pool detail queries, O(dashboard), O(missing_patches), and O(stats).
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
  - This module maps to the Xen Orchestra C(/pools), C(/pools/{id}), and selected
    C(/pools/{id}/{subresource}) endpoints.
  - The module validates unsupported parameter combinations before making the API call.
requirements:
  - python >= 3.9
"""

EXAMPLES = r"""
- name: List pools with selected fields
  w0.xen_orchestra.xoa_pool_info:
    api_host: xo.example.com
    username: admin
    password: secret
    fields:
      - uuid
      - name_label
      - master
    limit: 10

- name: Get a single pool by UUID
  w0.xen_orchestra.xoa_pool_info:
    api_host: xo.example.com
    username: admin
    password: secret
    pool_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c

- name: Get pool messages with selected fields
  w0.xen_orchestra.xoa_pool_info:
    api_host: xo.example.com
    username: admin
    password: secret
    pool_uuid: cef5f68c-61ae-3831-d2e6-1590d4934acf
    subresource: messages
    fields:
      - name
      - id
      - $object
    filter:
      - name:POOL_MASTER_CHANGED
    limit: 5

- name: Get pool alarms
  w0.xen_orchestra.xoa_pool_info:
    api_host: xo.example.com
    username: admin
    password: secret
    pool_uuid: f07ab729-c0e8-721c-45ec-f11276377030
    subresource: alarms
    fields:
      - id
      - time

- name: Get pool tasks with token authentication
  w0.xen_orchestra.xoa_pool_info:
    api_host: xo.example.com
    token: "{{ xo_token }}"
    pool_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c
    subresource: tasks
    filter:
      - status:failure
    limit: 5

- name: Get pool stats
  w0.xen_orchestra.xoa_pool_info:
    api_host: xo.example.com
    username: admin
    password: secret
    pool_uuid: f07ab729-c0e8-721c-45ec-f11276377030
    subresource: stats
    granularity: seconds

- name: Get pool dashboard
  w0.xen_orchestra.xoa_pool_info:
    api_host: xo.example.com
    username: admin
    password: secret
    pool_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c
    subresource: dashboard

- name: Get pool missing patches
  w0.xen_orchestra.xoa_pool_info:
    api_host: xo.example.com
    username: admin
    password: secret
    pool_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c
    subresource: missing_patches
"""

RETURN = r"""
result:
  description:
    - Data returned by the Xen Orchestra API.
    - The return shape depends on the request mode.
    - Pool collection queries return a list of pool records.
    - Pool detail queries return a single pool object.
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

POOL_SUBRESOURCES = {
    "alarms": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "dashboard": {"supported_params": {"ndjson"}},
    "messages": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "missing_patches": {"supported_params": set()},
    "stats": {"supported_params": {"granularity"}},
    "tasks": {"supported_params": STANDARD_COLLECTION_PARAMS},
}


def _validate_request_shape(module):

    pool_uuid = module.params["pool_uuid"]
    subresource = module.params["subresource"]

    if subresource and not pool_uuid:
        module.fail_json(msg="subresource requires pool_uuid")

    if subresource and subresource not in POOL_SUBRESOURCES:
        module.fail_json(msg=f"Invalid subresource: {subresource}")

    provided = provided_optional_params(module)
    allowed = allowed_request_parameters(POOL_SUBRESOURCES, pool_uuid, subresource)

    if not pool_uuid:
        allowed = STANDARD_COLLECTION_PARAMS
        label = "pool collection request"
    elif not subresource:
        allowed = set()
        label = "pool detail request"
    else:
        allowed = POOL_SUBRESOURCES[subresource]["supported_params"]
        label = f"pool subresource '{subresource}'"

    fail_on_unsupported_params(module, provided, allowed, label)


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            dict(
                pool_uuid=dict(type="str"),
                subresource=dict(type="str", choices=list(POOL_SUBRESOURCES.keys())),
                fields=dict(type="list", elements="str"),
                filter=dict(type="list", elements="str"),
                limit=dict(type="int"),
                ndjson=dict(type="bool"),
                markdown=dict(type="bool"),
                granularity=dict(type="str"),
            ),
        ),
        supports_check_mode=True,
    )

    validate_auth(module)
    _validate_request_shape(module)

    path = build_resource_path(module.params.get("pool_uuid"), module.params.get("subresource"))
    params = build_query_params(module)

    try:
        client = new_xoa_client(module)
        response, status_code = client.get("pools", path, params=params)

    except Exception as e:
        module.fail_json(msg=str(e))

    if status_code != 200:
        module.fail_json(msg=f"Unexpected status code: {status_code}")

    module.exit_json(changed=False, result=response)


if __name__ == "__main__":
    main()
