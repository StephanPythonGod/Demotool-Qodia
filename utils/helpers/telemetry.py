import os
from datetime import datetime

import streamlit as st
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from utils.helpers.logger import logger
from utils.helpers.otlp_connection import check_otlp_connection


class StreamlitTelemetryManager:
    def __init__(self):
        """Initialize telemetry manager."""
        self._telemetry_enabled = False
        self._meter_provider = None
        self._initialize_telemetry()
        self._define_metrics()

    def _initialize_telemetry(self):
        """Set up OTLP metrics exporter and meter provider."""
        try:
            service_name = f"{os.getenv('OTEL_SERVICE_NAME', 'Streamlit Frontend')} {os.getenv('DEPLOYMENT_ENV', 'staging')}"
            environment = os.getenv(
                "OTEL_RESOURCE_ATTRIBUTES", "deployment.environment=staging"
            ).split("=")[1]
            endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

            logger.info(f"Initializing telemetry for {service_name} in {environment}")

            success, formatted_endpoint = check_otlp_connection(endpoint)
            if not success:
                raise Exception("OTLP connection failed.")

            resource = Resource.create(
                {"service.name": service_name, "deployment.environment": environment}
            )
            otlp_metric_exporter = OTLPMetricExporter(
                endpoint=f"{formatted_endpoint}/v1/metrics"
            )
            metric_reader = PeriodicExportingMetricReader(
                otlp_metric_exporter, export_interval_millis=60000
            )

            self._meter_provider = MeterProvider(
                resource=resource, metric_readers=[metric_reader]
            )
            metrics.set_meter_provider(self._meter_provider)
            self._telemetry_enabled = True
            logger.info(
                f"Telemetry initialized successfully. Metrics will be exported to OTLP endpoint: {f'{formatted_endpoint}/v1/metrics'}"
            )
        except Exception as e:
            logger.error(f"Telemetry initialization failed: {e}", exc_info=True)
            self._telemetry_enabled = False

    def _define_metrics(self):
        """Define the metrics for telemetry."""
        try:
            if not self._telemetry_enabled:
                logger.warning("Telemetry is disabled; no metrics defined.")
                return

            meter = metrics.get_meter("Streamlit Metrics")
            self.feedback_duration_histogram = meter.create_histogram(
                "feedback_duration_seconds",
                description="Time taken by user to provide feedback after API response",
                unit="seconds",
            )
            self.feedback_time_total = meter.create_counter(
                "feedback_time_total_seconds",
                description="Total cumulative feedback time in seconds",
                unit="seconds",
            )
            logger.info("Metrics defined successfully.")
        except Exception as e:
            logger.error(f"Failed to define metrics: {e}", exc_info=True)

    def record_feedback_duration(self, feedback_start_time):
        """
        Record the feedback duration using the provided start time.
        :param feedback_start_time: The start time of the feedback session.
        """
        try:
            if not self._telemetry_enabled:
                logger.warning("Telemetry is disabled; feedback not recorded.")
                return
            if not feedback_start_time:
                logger.warning("Invalid start time; no duration recorded.")
                return

            # Calculate duration
            duration = (datetime.now() - feedback_start_time).total_seconds()

            # Record metrics with API key from Streamlit session state
            api_key = getattr(st.session_state, "api_key", "unknown")
            attributes = {"api_key": api_key}
            self.feedback_duration_histogram.record(duration, attributes)
            self.feedback_time_total.add(duration, attributes)

            logger.info(f"Feedback recorded: {duration} seconds for API key: {api_key}")
        except Exception as e:
            logger.error(f"Failed to record feedback duration: {e}", exc_info=True)

    def shutdown(self):
        """Shut down the telemetry resources."""
        if self._meter_provider:
            self._meter_provider.shutdown()
            self._meter_provider = None
            logger.info("Telemetry meter provider shut down successfully.")


def track_api_response():
    """
    Call this function when API results are received.
    Returns the current time for tracking feedback duration.

    Returns:
        datetime: The current time.
    """
    try:
        logger.info("API response tracked. Returning feedback start time.")
        return datetime.now()
    except Exception as e:
        logger.error(f"Failed to track API response: {e}", exc_info=True)
        return None


def track_user_feedback(feedback_start_time):
    """
    Call this function when the user submits feedback.
    Calculates and records the feedback duration.

    Args:
        feedback_start_time (datetime): The start time of the feedback session.
    """
    try:
        logger.info("Tracking user feedback.")
        manager = StreamlitTelemetryManager()
        manager.record_feedback_duration(feedback_start_time)
        logger.info("User feedback tracked successfully.")
    except Exception as e:
        logger.error(f"Failed to track user feedback: {e}", exc_info=True)
