from ansible.module_utils.basic import AnsibleModule
from ansible_collections.w0.xen_orchestra.plugins.module_utils.xoa import (  # type: ignore
    build_xoa_argument_spec,
    new_xoa_client,
    validate_auth,
)


def main():
    module = AnsibleModule(
        argument_spec=build_xoa_argument_spec(
            dict(
                vm_uuid=dict(type="str"),
                fields=dict(type="list"),
                filter=dict(type="list"),
                limit=dict(type="int"),
            )
        ),
    )

    validate_auth(module)

    if module.params["vm_uuid"]:
        path = module.params["vm_uuid"]
        params = None
    else:
        path = None

        fields = list(module.params["fields"] or [])
        filters = list(module.params["filter"] or [])

        params = dict(
            fields=",".join(fields),
            filter=" ".join(filters),
            limit=module.params["limit"],
        )

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
