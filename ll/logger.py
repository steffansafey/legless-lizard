import logging
import sys
from collections import namedtuple
from datetime import datetime

import structlog
from sentry_sdk import add_breadcrumb, capture_event
from sentry_sdk.utils import event_from_exception

SENTRY_EVENT_LEVEL = logging.WARNING
SENTRY_BREADCRUMB_LEVEL = logging.INFO

LogFilter = namedtuple("LogFilter", ["logger_name", "allowable_level"])

SENTRY_FILTERS = []


def setup_logging(log_level):
    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.StackInfoRenderer(),
        add_breadcrumbs_from_logs,
        capture_log_for_sentry,
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )

    # Output all logs to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    # Route all logs through structlog processors
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    root_logger.addHandler(stdout_handler)
    log_level = log_level.value
    root_logger.setLevel(getattr(logging, log_level))


def add_breadcrumbs_from_logs(_, __, event_dict):
    log_level = getattr(logging, event_dict["level"].upper())

    if log_level >= SENTRY_BREADCRUMB_LEVEL:
        additional_data = event_dict.copy()
        for removed_field in [
            "logger",
            "level",
            "event",
            "timestamp",
            "_record",
            "_from_structlog",
        ]:
            additional_data.pop(removed_field, None)

        crumb = {
            "type": "log",
            "level": event_dict.get("level", None),
            "category": event_dict.get("logger", None),
            "message": event_dict.get("event", None),
            "timestamp": datetime.fromisoformat(event_dict.get("timestamp", None)),
            "data": additional_data,
        }

        add_breadcrumb(crumb)

    return event_dict


def capture_log_for_sentry(_, __, event_dict):
    log_level = getattr(logging, event_dict["level"].upper())

    if log_level >= SENTRY_EVENT_LEVEL and not in_sentry_filters(event_dict):
        exc_info = event_dict.get("exc_info", False)
        if exc_info is True:
            # logger.exception() or logger.error(exc_info=True)
            exc_info = sys.exc_info()
        has_exc_info = exc_info and exc_info != (None, None, None)

        if has_exc_info:
            event, hint = event_from_exception(exc_info)
        else:
            event, hint = {}, None

        event["message"] = event_dict.get("event", None)
        event["level"] = event_dict.get("level", None)
        if "logger" in event_dict:
            event["logger"] = event_dict["logger"]

        event["extra"] = event_dict.copy()
        event["extra"].pop("event", None)

        sid = capture_event(event, hint=hint)

        event_dict["sentry_id"] = sid

    else:
        event_dict["sentry_id"] = None

    return event_dict


def in_sentry_filters(event_dict):
    disallow_sentry_capture = False

    event_logger = event_dict.get("logger", "")
    event_level = getattr(logging, event_dict["level"].upper())

    for log_filter in SENTRY_FILTERS:
        if (
            event_logger == log_filter.logger_name
            and event_level < log_filter.allowable_level
        ):
            disallow_sentry_capture = True

    return disallow_sentry_capture
