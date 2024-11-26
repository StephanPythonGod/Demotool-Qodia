import logging
import os
import sys
from typing import Optional, Tuple

from dotenv import load_dotenv
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import get_current_span

from utils.helpers.otlp_connection import check_otlp_connection

load_dotenv()


class OTELCompatibleLogHandler(LoggingHandler):
    """Logging handler that ensures OpenTelemetry compatibility"""

    def emit(self, record: logging.LogRecord) -> None:
        # Add trace context if available
        span = get_current_span()
        if span:
            span_context = span.get_span_context()
            setattr(record, "trace_id", f"{span_context.trace_id:032x}")
            setattr(record, "span_id", f"{span_context.span_id:016x}")
        else:
            setattr(record, "trace_id", "0" * 32)
            setattr(record, "span_id", "0" * 16)

        try:
            super().emit(record)
        except Exception as e:
            print(f"[ERROR] Exception during OTEL log emit: {e}")
            self.handleError(record)


def initialize_otlp_logging() -> Tuple[Optional[LoggerProvider], bool]:
    """Initialize OTLP logging and return (provider, success)"""
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    success, formatted_endpoint = check_otlp_connection(otlp_endpoint)
    if not success:
        logging.warning("OTLP endpoint not accessible, skipping OTLP initialization")
        return None, False

    try:
        resource = Resource.create(
            {
                "service.name": f"{os.getenv('OTEL_SERVICE_NAME', 'Qodia Kodierungstool')} {os.getenv('DEPLOYMENT_ENV', 'staging')}",
                "deployment.environment": os.getenv("DEPLOYMENT_ENV", "staging"),
            }
        )
        log_provider = LoggerProvider(resource=resource)
        otlp_exporter = OTLPLogExporter(
            endpoint=f"{formatted_endpoint}/v1/logs",
        )
        log_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))
        set_logger_provider(log_provider)
        return log_provider, True
    except Exception as e:
        logging.warning(f"Failed to initialize OTLP logging: {e}")
        return None, False


def setup_logger(
    name: str = "qodia_koodierungstool",
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger for the application.
    This function configures a logger with the specified name, log level,
    format, and optional file output.

    Args:
        name (str): The name of the logger. Defaults to "qodia_koodierungstool".
        level (int): The logging level. Defaults to logging.INFO.
        log_format (Optional[str]): The log message format. If None, a default format is used.
        log_file (Optional[str]): The path to a log file. If provided, logs will be written to this file.

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(name)

    # TODO: Remove this once the issue is fixed
    logging.getLogger("torch.classes").setLevel(logging.ERROR)

    # Prevent adding handlers multiple times
    if not logger.hasHandlers():
        logger.setLevel(level)

        # Use default format if none is provided
        if log_format is None:
            log_format = "%(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)

        # Create console handler and set level
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # If a log file is specified, add a file handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Initialize OTLP logging
        log_provider, otlp_enabled = initialize_otlp_logging()
        if otlp_enabled and log_provider is not None:
            otel_handler = OTELCompatibleLogHandler(level=level)
            otel_handler.setFormatter(formatter)
            logger.addHandler(otel_handler)
        else:
            logger.warning("OTLP logging initialization failed")

    return logger


# Create and configure logger
logger = setup_logger()
