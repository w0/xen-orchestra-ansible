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
