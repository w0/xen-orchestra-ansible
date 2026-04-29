STANDARD_COLLECTION_PARAMS = {"fields", "filter", "limit", "ndjson", "markdown"}


def build_resource_path(object_id=None, subresource=None):
    if not object_id:
        return None
    if not subresource:
        return object_id
    return f"{object_id}/{subresource}"


def allowed_request_parameters(subresources: dict, object_id=None, subresource=None):
    if not object_id:
        # No object_id, assume collection-level request
        return STANDARD_COLLECTION_PARAMS

    if not subresource:
        # No subresource, assume object-level request
        return set()

    return subresources[subresource].get("supported_params")


def build_query_params(module):
    params = {}

    if module.params["fields"]:
        params["fields"] = ",".join(module.params["fields"])
    if module.params["filter"]:
        params["filter"] = " ".join(module.params["filter"])
    if module.params["limit"] is not None:
        params["limit"] = module.params["limit"]
    if module.params["ndjson"] is not None:
        params["ndjson"] = module.params["ndjson"]
    if module.params["markdown"] is not None:
        params["markdown"] = module.params["markdown"]
    if module.params["granularity"]:
        params["granularity"] = module.params["granularity"]

    return params or None


def fail_on_unsupported_params(module, provided, allowed, label):
    unsupported = sorted(provided - allowed)
    if unsupported:
        module.fail_json(msg=f"Unsupported parameters for {label}: {', '.join(unsupported)}")
