import structlog


def add_service(service_name: str):
    def processor(_, __, event_dict):
        event_dict["service.name"] = service_name
        return event_dict

    return processor


def add_request_context(_, __, event_dict):
    context_vars = structlog.contextvars.get_contextvars()

    request_fields = [
        "http.request.id",
        "trace.id",
        "user.id",
        "user.roles",
        "http.request.method",
        "url.path",
        "url.route",
        "client.address",
        "user_agent.original",
    ]

    for field in request_fields:
        if field in context_vars:
            event_dict[field] = context_vars[field]

    return event_dict


def rename_level_key(_, __, event_dict):
    if "level" in event_dict:
        event_dict["log.level"] = event_dict.pop("level")
    return event_dict


def rename_event_key(_, __, event_dict):
    if "event" in event_dict:
        event_dict["message"] = event_dict.pop("event")
    return event_dict
