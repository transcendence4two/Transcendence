import structlog


def add_service(service_name: str):
    def processor(_, __, event_dict):
        event_dict["service"] = service_name
        return event_dict

    return processor


def add_request_context(_, __, event_dict):
    context_vars = structlog.contextvars.get_contextvars()

    request_fields = [
        "request_id",
        "trace_id",
        "user_id",
        "user_roles",
        "method",
        "path",
        "route",
        "client_host",
        "user_agent",
    ]

    for field in request_fields:
        if field in context_vars:
            event_dict[field] = context_vars[field]

    return event_dict
