#!/usr/bin/python

DOCUMENTATION = r"""
---
module: xoa_user_info
short_description: Gather information about Xen Orchestra users
description:
  - Gather information about users through the Xen Orchestra REST API.
  - When O(user_uuid) is omitted, the module queries the user collection endpoint and can
    filter, limit, and select fields from the returned user list.
  - When O(user_uuid) is provided without O(subresource), the module returns detailed
    information for the user identified by O(user_uuid).
  - When both O(user_uuid) and O(subresource) are provided, the module returns the
    requested subresource for that user.
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
  user_uuid:
    description:
      - UUID of the user to query.
      - When omitted, the module queries the user collection endpoint.
      - Required when O(subresource) is specified.
    type: str
  subresource:
    description:
      - User subresource to query for the user identified by O(user_uuid).
      - The module validates subresource-specific query parameters before making the API call.
      - O(groups) and O(tasks) support O(fields), O(filter), O(limit), O(ndjson), and
        O(markdown).
      - O(acl-privileges) supports O(fields), O(filter), O(limit), and O(ndjson).
      - O(authentication_tokens) supports O(filter) and O(limit).
    type: str
    choices:
      - acl-privileges
      - authentication_tokens
      - groups
      - tasks
  fields:
    description:
      - List of fields to request from the Xen Orchestra API.
      - Values are joined with commas before being sent to Xen Orchestra.
      - Supported for user collection queries and for the O(acl-privileges), O(groups),
        and O(tasks) subresources.
      - Ignored for user detail queries.
    type: list
    elements: str
  filter:
    description:
      - List of filter expressions to apply to the API request.
      - Values are joined with spaces before being sent to Xen Orchestra.
      - Filter syntax is defined by the Xen Orchestra REST API.
      - Supported for user collection queries and for all user subresources.
      - Ignored for user detail queries.
    type: list
    elements: str
  limit:
    description:
      - Maximum number of objects to return.
      - Supported for user collection queries and for all user subresources.
      - Ignored for user detail queries.
    type: int
  ndjson:
    description:
      - Request newline-delimited JSON output from the API when supported.
      - Supported for user collection queries and for the O(acl-privileges), O(groups),
        and O(tasks) subresources.
      - Ignored for user detail queries.
      - Ignored for O(authentication_tokens).
    type: bool
  markdown:
    description:
      - Request markdown output from the API when supported.
      - Supported for user collection queries and for the O(groups) and O(tasks)
        subresources.
      - Ignored for user detail queries.
      - Ignored for O(acl-privileges) and O(authentication_tokens).
    type: bool
notes:
  - Authentication must be either C(token) alone or C(username) and C(password) together.
  - This module maps to the Xen Orchestra C(/users), C(/users/{id}), and selected
    C(/users/{id}/{subresource}) endpoints.
  - The module validates unsupported parameter combinations before making the API call.
requirements:
  - python >= 3.9
"""

EXAMPLES = r"""
- name: List users with selected fields
  w0.xen_orchestra.xoa_user_info:
    api_host: xo.example.com
    username: admin
    password: secret
    fields:
      - id
      - email
      - permission
    limit: 10

- name: Get a single user by UUID
  w0.xen_orchestra.xoa_user_info:
    api_host: xo.example.com
    username: admin
    password: secret
    user_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c

- name: Get groups for a user
  w0.xen_orchestra.xoa_user_info:
    api_host: xo.example.com
    username: admin
    password: secret
    user_uuid: cef5f68c-61ae-3831-d2e6-1590d4934acf
    subresource: groups
    fields:
      - id
      - name
    limit: 5

- name: Get user tasks with token authentication
  w0.xen_orchestra.xoa_user_info:
    api_host: xo.example.com
    token: "{{ xo_token }}"
    user_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c
    subresource: tasks
    filter:
      - status:failure
    limit: 5

- name: Get authentication tokens for a user
  w0.xen_orchestra.xoa_user_info:
    api_host: xo.example.com
    username: admin
    password: secret
    user_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c
    subresource: authentication_tokens
    filter:
      - active:true
    limit: 5

- name: Get ACL privileges for a user
  w0.xen_orchestra.xoa_user_info:
    api_host: xo.example.com
    username: admin
    password: secret
    user_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c
    subresource: acl-privileges
"""

RETURN = r"""
result:
  description:
    - Data returned by the Xen Orchestra API.
    - The return shape depends on the request mode.
    - User collection queries return a list of user records.
    - User detail queries return a single user object.
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

USER_SUBRESOURCES = {
    "acl-privileges": {"supported_params": {"id", "fields", "ndjson", "filter", "limit"}},
    "authentication_tokens": {"supported_params": {"id", "filter", "limit"}},
    "groups": {"supported_params": STANDARD_COLLECTION_PARAMS},
    "tasks": {"supported_params": STANDARD_COLLECTION_PARAMS},
}


def _validate_request_shape(module):

    user_uuid = module.params["user_uuid"]
    subresource = module.params["subresource"]

    if subresource and not user_uuid:
        module.fail_json(msg="subresource requires user_uuid")

    if subresource and subresource not in USER_SUBRESOURCES:
        module.fail_json(msg=f"Invalid subresource: {subresource}")

    provided = provided_optional_params(module)
    allowed = allowed_request_parameters(USER_SUBRESOURCES, user_uuid, subresource)

    if not user_uuid:
        allowed = STANDARD_COLLECTION_PARAMS
        label = "user collection request"
    elif not subresource:
        allowed = set()
        label = "user detail request"
    else:
        allowed = USER_SUBRESOURCES[subresource]["supported_params"]
        label = f"user subresource '{subresource}'"

    fail_on_unsupported_params(module, provided, allowed, label)


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            user_uuid=dict(type="str"),
            subresource=dict(type="str", choices=list(USER_SUBRESOURCES.keys())),
            fields=dict(type="list", elements="str"),
            filter=dict(type="list", elements="str"),
            limit=dict(type="int"),
            ndjson=dict(type="bool"),
            markdown=dict(type="bool"),
        )
    )

    validate_auth(module)
    _validate_request_shape(module)

    path = build_resource_path(module.params["user_uuid"], module.params["subresource"])
    params = build_query_params(module)

    try:
        client = new_xoa_client(module)
        response, status_code = client.get("users", path, params=params)

    except Exception as e:
        module.fail_json(msg=str(e))

    if status_code != 200:
        module.fail_json(msg=f"Unexpected status code: {status_code}")

    module.exit_json(changed=False, result=response)


if __name__ == "__main__":
    main()
