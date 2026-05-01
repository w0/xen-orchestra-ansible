#!/usr/bin/python

DOCUMENTATION = r"""
---
module: xoa_backup_job_info
short_description: Gather information about Xen Orchestra backup jobs
description:
  - Gather information about backup jobs through the Xen Orchestra REST API.
  - When O(backup_job_uuid) is omitted, the module queries the backup job collection
    endpoint and can filter, limit, and select fields from the returned backup job list.
  - When O(backup_job_uuid) is provided, the module returns detailed information for the
    backup job identified by O(backup_job_uuid).
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
  backup_job_uuid:
    description:
      - UUID of the backup job to query.
      - When omitted, the module queries the backup job collection endpoint.
    type: str
  fields:
    description:
      - List of fields to request from the Xen Orchestra API.
      - Values are joined with commas before being sent to Xen Orchestra.
      - Supported for backup job collection queries.
      - Ignored for backup job detail queries.
    type: list
    elements: str
  filter:
    description:
      - List of filter expressions to apply to the API request.
      - Values are joined with spaces before being sent to Xen Orchestra.
      - Filter syntax is defined by the Xen Orchestra REST API.
      - Supported for backup job collection queries.
      - Ignored for backup job detail queries.
    type: list
    elements: str
  limit:
    description:
      - Maximum number of objects to return.
      - Supported for backup job collection queries.
      - Ignored for backup job detail queries.
    type: int
  ndjson:
    description:
      - Request newline-delimited JSON output from the API when supported.
      - Supported for backup job collection queries.
      - Ignored for backup job detail queries.
    type: bool
  markdown:
    description:
      - Request markdown output from the API when supported.
      - Supported for backup job collection queries.
      - Ignored for backup job detail queries.
    type: bool
notes:
  - Authentication must be either C(token) alone or C(username) and C(password) together.
  - This module maps to the Xen Orchestra C(/backup-jobs) and
    C(/backup-jobs/{id}) endpoints.
  - The module validates unsupported parameter combinations before making the API call.
requirements:
  - python >= 3.9
"""

EXAMPLES = r"""
- name: List backup jobs with selected fields
  w0.xen_orchestra.xoa_backup_job_info:
    api_host: xo.example.com
    username: admin
    password: secret
    fields:
      - id
      - uuid
    limit: 10

- name: Get a single backup job by UUID
  w0.xen_orchestra.xoa_backup_job_info:
    api_host: xo.example.com
    username: admin
    password: secret
    backup_job_uuid: 613f541c-4bed-fc77-7ca8-2db6b68f079c

- name: List backup jobs with token authentication
  w0.xen_orchestra.xoa_backup_job_info:
    api_host: xo.example.com
    token: "{{ xo_token }}"
    filter:
      - mode:delta
    limit: 5
"""

RETURN = r"""
result:
  description:
    - Data returned by the Xen Orchestra API.
    - The return shape depends on the request mode.
    - Backup job collection queries return a list of backup job records.
    - Backup job detail queries return a single backup job object.
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
    build_query_params,
    build_resource_path,
    fail_on_unsupported_params,
    provided_optional_params,
)


def _validate_request_shape(module):

    backup_job_uuid = module.params["backup_job_uuid"]

    provided = provided_optional_params(module)

    if not backup_job_uuid:
        allowed = STANDARD_COLLECTION_PARAMS
        label = "backup_job collection request"
    else:
        allowed = set()
        label = "backup_job detail request"

    fail_on_unsupported_params(module, provided, allowed, label)


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            backup_job_uuid=dict(type="str"),
            fields=dict(type="list", elements="str"),
            filter=dict(type="list", elements="str"),
            limit=dict(type="int"),
            ndjson=dict(type="bool"),
            markdown=dict(type="bool"),
        )
    )

    validate_auth(module)
    _validate_request_shape(module)

    path = build_resource_path(module.params["backup_job_uuid"], module.params["subresource"])
    params = build_query_params(module)

    try:
        client = new_xoa_client(module)
        response, status_code = client.get("backup-jobs", path, params=params)

    except Exception as e:
        module.fail_json(msg=str(e))

    if status_code != 200:
        module.fail_json(msg=f"Unexpected status code: {status_code}")

    module.exit_json(changed=False, result=response)


if __name__ == "__main__":
    main()
